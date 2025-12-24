import java.awt.*;
import java.awt.event.*;
import java.io.*;
import java.net.*;
import java.util.*;
import java.util.List;
import java.util.concurrent.*;
import javax.swing.*;

/* ============================================================
   SAMSOFT! LIVE! PLAY 1.0
   "Download-play" style host/join + LAN discovery + arcade menu
   Single-file Java 17+ prototype

   Notes:
   - This is NOT Nintendo DS "Download Play". It is a generic LAN
     discovery + server-sends-bundle flow for your Java game.
   - No external assets/files; everything is drawn procedurally.
   ============================================================ */

public class SML {

    /* ===================== CONFIG ===================== */
    static final int SCREEN_W = 800;
    static final int SCREEN_H = 600;

    static final int SERVER_PORT = 7777;
    static final int DISCOVERY_PORT = 7778;

    static final String APP_TITLE = "Samsoft! Live! Play 1.0";
    static final String GAME_TITLE = "MARIO! LIVE";
    static final String NET_MAGIC = "SML";

    /* ===================== STATE ===================== */
    enum Scene {
        MAIN_MENU,
        ONLINE_MENU,
        JOIN_BROWSER,
        OPTIONS,
        LOBBY,
        PLAYING
    }

    static volatile Scene scene = Scene.MAIN_MENU;

    /* ===================== NETWORK ===================== */
    enum PacketType {
        HANDSHAKE,
        HANDSHAKE_ACK,
        DOWNLOAD_BUNDLE,
        PLAYER_UPDATE,
        CHAT,
        HEARTBEAT
    }

    static record Packet(PacketType type, Object payload) implements Serializable {}

    static class Handshake implements Serializable {
        final String playerName;
        final String clientVersion;
        Handshake(String playerName, String clientVersion) {
            this.playerName = playerName;
            this.clientVersion = clientVersion;
        }
    }

    static class ServerInfo implements Serializable {
        final String serverName;
        final String version;
        final String gameId;
        ServerInfo(String serverName, String version, String gameId) {
            this.serverName = serverName;
            this.version = version;
            this.gameId = gameId;
        }
    }

    static class GameBundle implements Serializable {
        final String gameId;
        final List<String> levels;
        final String motd;
        GameBundle(String gameId, List<String> levels, String motd) {
            this.gameId = gameId;
            this.levels = levels;
            this.motd = motd;
        }
    }

    /* ===================== GAME DATA ===================== */
    static class Stats implements Serializable {
        int hp = 100;
        int mp = 50;
        int attack = 10;
        int defense = 5;
        int level = 1;
    }

    static class Player implements Serializable {
        String name;
        float x = 100;
        float y = 320;
        Stats stats = new Stats();

        Player(String name) {
            this.name = name;
        }
    }

    enum ZoneType { OVERWORLD, DUNGEON, TOWN }

    static class Zone {
        final String id;
        final ZoneType type;
        final Set<String> players = ConcurrentHashMap.newKeySet();

        Zone(String id, ZoneType type) {
            this.id = id;
            this.type = type;
        }
    }

    /* ===================== ROM ADAPTER ===================== */
    static class RomAdapter {
        final Map<String, List<String>> extractedLevels = new ConcurrentHashMap<>();

        void loadGameData(String gameId) {
            System.out.println("[ROM] Loading metadata for " + gameId);
            extractedLevels.put(gameId, List.of("Town", "Dungeon", "Castle"));
        }

        GameBundle buildBundle(String gameId) {
            List<String> lvls = extractedLevels.getOrDefault(gameId, List.of("Town"));
            return new GameBundle(gameId, lvls, "Welcome to " + GAME_TITLE + " - " + APP_TITLE);
        }
    }

    /* ===================== SERVER ===================== */
    static class DownloadPlayServer {
        private final RomAdapter rom;
        private final String gameId;

        private volatile boolean running;
        private ServerSocket server;
        private final Map<String, ClientHandler> clients = new ConcurrentHashMap<>();

        DownloadPlayServer(RomAdapter rom, String gameId) {
            this.rom = rom;
            this.gameId = gameId;
        }

        void start() throws IOException {
            if (running) return;
            running = true;

            server = new ServerSocket(SERVER_PORT);

            Thread accept = new Thread(this::acceptLoop, "sml-accept");
            accept.setDaemon(true);
            accept.start();

            Thread beacon = new Thread(this::broadcastBeaconLoop, "sml-beacon");
            beacon.setDaemon(true);
            beacon.start();

            System.out.println("[SERVER] Online at port " + SERVER_PORT);
        }

        void stop() {
            running = false;
            try { if (server != null) server.close(); } catch (IOException ignored) {}
            for (ClientHandler c : clients.values()) {
                try { c.close(); } catch (IOException ignored) {}
            }
            clients.clear();
        }

        int clientCount() {
            return clients.size();
        }

        private void acceptLoop() {
            while (running) {
                try {
                    Socket socket = server.accept();
                    socket.setTcpNoDelay(true);

                    ClientHandler handler = new ClientHandler(socket);
                    clients.put(socket.getRemoteSocketAddress().toString(), handler);

                    Thread t = new Thread(handler, "sml-client-" + socket.getPort());
                    t.setDaemon(true);
                    t.start();
                } catch (IOException ignored) {
                    // server socket closed / stopped
                }
            }
        }

        private void broadcastBeaconLoop() {
            // LAN discovery beacon
            try (DatagramSocket socket = new DatagramSocket()) {
                socket.setBroadcast(true);
                while (running) {
                    // Format: SML|players|serverPort|version
                    String msg = NET_MAGIC + "|" + clients.size() + "|" + SERVER_PORT + "|" + APP_TITLE;
                    byte[] data = msg.getBytes();
                    DatagramPacket packet = new DatagramPacket(
                            data,
                            data.length,
                            InetAddress.getByName("255.255.255.255"),
                            DISCOVERY_PORT
                    );
                    socket.send(packet);
                    Thread.sleep(750);
                }
            } catch (Exception ignored) {
            }
        }

        class ClientHandler implements Runnable {
            private final Socket socket;
            private ObjectInputStream in;
            private ObjectOutputStream out;
            private volatile boolean alive = true;

            ClientHandler(Socket socket) {
                this.socket = socket;
            }

            @Override
            public void run() {
                try {
                    // IMPORTANT: create ObjectOutputStream first, flush, then ObjectInputStream (avoids deadlock)
                    out = new ObjectOutputStream(socket.getOutputStream());
                    out.flush();
                    in = new ObjectInputStream(socket.getInputStream());

                    while (running && alive) {
                        Object obj = in.readObject();
                        if (!(obj instanceof Packet p)) continue;
                        handle(p);
                    }
                } catch (Exception e) {
                    // client disconnect
                } finally {
                    clients.remove(socket.getRemoteSocketAddress().toString());
                    try { close(); } catch (IOException ignored) {}
                }
            }

            void handle(Packet packet) throws IOException {
                if (packet.type == PacketType.HANDSHAKE) {
                    Handshake hs = (packet.payload instanceof Handshake h) ? h : new Handshake("Player", "?");

                    // Ack
                    send(this, new Packet(PacketType.HANDSHAKE_ACK,
                            new ServerInfo("Samsoft Host", APP_TITLE, gameId)));

                    // "Download play" bundle: server sends level list & MOTD
                    GameBundle bundle = rom.buildBundle(gameId);
                    send(this, new Packet(PacketType.DOWNLOAD_BUNDLE, bundle));

                    System.out.println("[SERVER] Handshake from " + hs.playerName + " (" + hs.clientVersion + ")");
                    return;
                }

                // For now, simply relay everything else
                broadcast(packet);
            }

            void close() throws IOException {
                alive = false;
                try { if (in != null) in.close(); } catch (IOException ignored) {}
                try { if (out != null) out.close(); } catch (IOException ignored) {}
                if (socket != null && !socket.isClosed()) socket.close();
            }
        }

        void broadcast(Packet packet) {
            for (ClientHandler c : clients.values()) {
                try {
                    send(c, packet);
                } catch (IOException e) {
                    clients.remove(c.socket.getRemoteSocketAddress().toString());
                    try { c.close(); } catch (IOException ignored) {}
                }
            }
        }

        private void send(ClientHandler c, Packet packet) throws IOException {
            if (c.out == null) return;
            synchronized (c.out) {
                c.out.writeObject(packet);
                c.out.flush();
            }
        }
    }

    /* ===================== CLIENT ===================== */
    static class DownloadPlayClient {
        private Socket socket;
        private ObjectInputStream in;
        private ObjectOutputStream out;
        private volatile boolean running;

        volatile ServerInfo serverInfo;
        volatile GameBundle bundle;

        void connect(InetAddress host, String playerName) throws IOException {
            disconnect();
            socket = new Socket(host, SERVER_PORT);
            socket.setTcpNoDelay(true);

            // IMPORTANT: create ObjectOutputStream first, flush, then ObjectInputStream
            out = new ObjectOutputStream(socket.getOutputStream());
            out.flush();
            in = new ObjectInputStream(socket.getInputStream());

            running = true;

            // handshake
            send(new Packet(PacketType.HANDSHAKE, new Handshake(playerName, APP_TITLE)));

            Thread reader = new Thread(this::readLoop, "sml-client-read");
            reader.setDaemon(true);
            reader.start();
        }

        private void readLoop() {
            try {
                while (running) {
                    Object obj = in.readObject();
                    if (!(obj instanceof Packet p)) continue;

                    if (p.type == PacketType.HANDSHAKE_ACK && p.payload instanceof ServerInfo si) {
                        serverInfo = si;
                    } else if (p.type == PacketType.DOWNLOAD_BUNDLE && p.payload instanceof GameBundle b) {
                        bundle = b;
                    }
                }
            } catch (Exception ignored) {
            } finally {
                disconnect();
            }
        }

        void send(Packet p) throws IOException {
            if (out == null) return;
            synchronized (out) {
                out.writeObject(p);
                out.flush();
            }
        }

        void disconnect() {
            running = false;
            try { if (in != null) in.close(); } catch (IOException ignored) {}
            try { if (out != null) out.close(); } catch (IOException ignored) {}
            try { if (socket != null) socket.close(); } catch (IOException ignored) {}
            socket = null;
            in = null;
            out = null;
        }
    }

    /* ===================== DISCOVERY ===================== */
    static class ServerListing {
        final InetAddress address;
        final int players;
        final int port;
        final String label;
        final long lastSeenMs;

        ServerListing(InetAddress address, int players, int port, String label, long lastSeenMs) {
            this.address = address;
            this.players = players;
            this.port = port;
            this.label = label;
            this.lastSeenMs = lastSeenMs;
        }

        String displayLine() {
            return address.getHostAddress() + ":" + port + "  |  " + players + " players  |  " + label;
        }
    }

    static class DiscoveryClient {
        private final ConcurrentHashMap<String, ServerListing> servers = new ConcurrentHashMap<>();
        private volatile boolean running;

        void start() {
            if (running) return;
            running = true;

            Thread t = new Thread(this::listenLoop, "sml-discovery");
            t.setDaemon(true);
            t.start();
        }

        void stop() {
            running = false;
        }

        List<ServerListing> snapshot() {
            long now = System.currentTimeMillis();
            // prune stale (not seen for 4 seconds)
            servers.entrySet().removeIf(e -> now - e.getValue().lastSeenMs > 4000);

            List<ServerListing> list = new ArrayList<>(servers.values());
            list.sort(Comparator.comparing(a -> a.address.getHostAddress()));
            return list;
        }

        private void listenLoop() {
            byte[] buf = new byte[512];
            try (DatagramSocket socket = new DatagramSocket(DISCOVERY_PORT)) {
                socket.setSoTimeout(800);
                while (running) {
                    try {
                        DatagramPacket p = new DatagramPacket(buf, buf.length);
                        socket.receive(p);

                        String msg = new String(p.getData(), 0, p.getLength()).trim();
                        // Format: SML|players|serverPort|version
                        String[] parts = msg.split("\\|");
                        if (parts.length < 4) continue;
                        if (!NET_MAGIC.equals(parts[0])) continue;

                        int players = safeInt(parts[1], 0);
                        int port = safeInt(parts[2], SERVER_PORT);
                        String label = parts[3];

                        String key = p.getAddress().getHostAddress() + ":" + port;
                        servers.put(key, new ServerListing(p.getAddress(), players, port, label, System.currentTimeMillis()));
                    } catch (SocketTimeoutException ignored) {
                        // just loop
                    } catch (Exception ignored) {
                        // malformed packet
                    }
                }
            } catch (Exception ignored) {
            }
        }

        private static int safeInt(String s, int fallback) {
            try { return Integer.parseInt(s.trim()); } catch (Exception e) { return fallback; }
        }
    }

    /* ===================== HUD ===================== */
    static class GameHUD {
        void render(Graphics2D g, Player p) {
            g.setColor(new Color(20, 20, 40, 220));
            g.fillRoundRect(12, 12, 260, 60, 12, 12);

            // HP bar
            g.setColor(new Color(220, 40, 40));
            g.fillRoundRect(24, 26, Math.max(0, Math.min(200, p.stats.hp * 2)), 16, 10, 10);
            g.setColor(Color.WHITE);
            g.drawRoundRect(24, 26, 200, 16, 10, 10);
            g.drawString("HP " + p.stats.hp + "/100", 232, 39);

            // MP bar
            g.setColor(new Color(60, 140, 255));
            g.fillRoundRect(24, 46, Math.max(0, Math.min(200, p.stats.mp * 4)), 10, 10, 10);
            g.setColor(Color.WHITE);
            g.drawRoundRect(24, 46, 200, 10, 10, 10);
        }
    }

    /* ===================== PANEL ===================== */
    static class GamePanel extends JPanel implements Runnable {
        // Game
        final Player player = new Player("Player1");
        final GameHUD hud = new GameHUD();

        // Assets / style
        final Font logoFont = new Font("SansSerif", Font.BOLD, 60);
        final Font subLogoFont = new Font("SansSerif", Font.BOLD, 18);
        final Font menuFont = new Font("SansSerif", Font.BOLD, 22);
        final Font smallFont = new Font("SansSerif", Font.PLAIN, 14);

        // Menu model
        int mainIndex = 0;
        int onlineIndex = 0;
        int joinIndex = 0;

        final String[] mainItems = {
                "LOCAL PLAY",
                "ONLINE PLAY",
                "OPTIONS",
                "QUIT"
        };

        final String[] onlineItems = {
                "HOST (LAN)",
                "JOIN (LAN)",
                "BACK"
        };

        // Networking
        final RomAdapter rom;
        final String gameId;
        DownloadPlayServer server;
        final DownloadPlayClient client = new DownloadPlayClient();
        final DiscoveryClient discovery = new DiscoveryClient();

        // Anim
        long startMs = System.currentTimeMillis();
        float shimmer = 0;

        // Loop
        volatile boolean running = true;

        GamePanel(RomAdapter rom, String gameId) {
            this.rom = rom;
            this.gameId = gameId;

            setPreferredSize(new Dimension(SCREEN_W, SCREEN_H));
            setFocusable(true);

            discovery.start();

            addKeyListener(new KeyAdapter() {
                @Override
                public void keyPressed(KeyEvent e) {
                    handleKeyPressed(e);
                }
            });

            Thread t = new Thread(this, "sml-render");
            t.setDaemon(true);
            t.start();
        }

        @Override
        public void addNotify() {
            super.addNotify();
            requestFocusInWindow();
        }

        void handleKeyPressed(KeyEvent e) {
            int k = e.getKeyCode();

            // Global back
            if (k == KeyEvent.VK_ESCAPE) {
                switch (scene) {
                    case MAIN_MENU -> System.exit(0);
                    case ONLINE_MENU -> scene = Scene.MAIN_MENU;
                    case JOIN_BROWSER -> scene = Scene.ONLINE_MENU;
                    case OPTIONS -> scene = Scene.MAIN_MENU;
                    case LOBBY -> {
                        // stop networking and go back
                        if (client != null) client.disconnect();
                        if (server != null) server.stop();
                        scene = Scene.MAIN_MENU;
                    }
                    case PLAYING -> scene = Scene.LOBBY;
                }
                return;
            }

            // Menu navigation
            if (scene == Scene.MAIN_MENU) {
                if (k == KeyEvent.VK_UP) mainIndex = (mainIndex + mainItems.length - 1) % mainItems.length;
                if (k == KeyEvent.VK_DOWN) mainIndex = (mainIndex + 1) % mainItems.length;
                if (k == KeyEvent.VK_ENTER) {
                    switch (mainIndex) {
                        case 0 -> { // local
                            // local: no networking, straight into lobby
                            if (server != null) server.stop();
                            client.disconnect();
                            scene = Scene.LOBBY;
                        }
                        case 1 -> scene = Scene.ONLINE_MENU;
                        case 2 -> scene = Scene.OPTIONS;
                        case 3 -> System.exit(0);
                    }
                }
                return;
            }

            if (scene == Scene.ONLINE_MENU) {
                if (k == KeyEvent.VK_UP) onlineIndex = (onlineIndex + onlineItems.length - 1) % onlineItems.length;
                if (k == KeyEvent.VK_DOWN) onlineIndex = (onlineIndex + 1) % onlineItems.length;
                if (k == KeyEvent.VK_ENTER) {
                    switch (onlineIndex) {
                        case 0 -> { // host
                            try {
                                if (server == null) server = new DownloadPlayServer(rom, gameId);
                                server.start();
                                client.disconnect();
                                scene = Scene.LOBBY;
                            } catch (IOException ex) {
                                // if hosting fails, just stay in menu
                                System.out.println("[SERVER] Failed to start: " + ex);
                            }
                        }
                        case 1 -> { // join
                            joinIndex = 0;
                            scene = Scene.JOIN_BROWSER;
                        }
                        case 2 -> scene = Scene.MAIN_MENU;
                    }
                }
                return;
            }

            if (scene == Scene.JOIN_BROWSER) {
                List<ServerListing> list = discovery.snapshot();
                if (k == KeyEvent.VK_UP) {
                    joinIndex = list.isEmpty() ? 0 : (joinIndex + list.size() - 1) % list.size();
                }
                if (k == KeyEvent.VK_DOWN) {
                    joinIndex = list.isEmpty() ? 0 : (joinIndex + 1) % list.size();
                }
                if (k == KeyEvent.VK_ENTER) {
                    if (!list.isEmpty()) {
                        ServerListing pick = list.get(Math.max(0, Math.min(joinIndex, list.size() - 1)));
                        try {
                            if (server != null) server.stop();
                            client.connect(pick.address, player.name);
                            scene = Scene.LOBBY;
                        } catch (IOException ex) {
                            System.out.println("[CLIENT] Failed to connect: " + ex);
                        }
                    }
                }
                return;
            }

            if (scene == Scene.LOBBY) {
                if (k == KeyEvent.VK_ENTER) {
                    scene = Scene.PLAYING;
                }
                return;
            }

            // Gameplay input
            if (scene == Scene.PLAYING) {
                switch (k) {
                    case KeyEvent.VK_LEFT -> player.x -= 6;
                    case KeyEvent.VK_RIGHT -> player.x += 6;
                    case KeyEvent.VK_UP -> player.y -= 6;
                    case KeyEvent.VK_DOWN -> player.y += 6;
                }
            }
        }

        @Override
        public void run() {
            long last = System.nanoTime();
            while (running) {
                long now = System.nanoTime();
                float dt = (now - last) / 1_000_000_000f;
                last = now;
                shimmer += dt;

                // keep player on-screen
                player.x = clamp(player.x, 0, SCREEN_W - 32);
                player.y = clamp(player.y, 60, SCREEN_H - 32);

                repaint();
                try { Thread.sleep(16); } catch (InterruptedException ignored) {}
            }
        }

        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            Graphics2D g2 = (Graphics2D) g.create();
            g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

            if (scene == Scene.PLAYING) {
                drawGame(g2);
            } else {
                drawMenuLikeMelee(g2);
            }

            g2.dispose();
        }

        /* ---------------- MENU LOOK ---------------- */
        void drawMenuLikeMelee(Graphics2D g2) {
            // Dark base
            g2.setColor(new Color(10, 10, 14));
            g2.fillRect(0, 0, SCREEN_W, SCREEN_H);

            // "Melee-ish" sweeping light band
            float t = shimmer;
            int bandW = 220;
            int cx = (int) ((Math.sin(t * 0.7) * 0.5 + 0.5) * (SCREEN_W + bandW) - bandW / 2f);
            GradientPaint gp = new GradientPaint(cx, 0, new Color(255, 255, 255, 0), cx + bandW, 0, new Color(255, 255, 255, 50));
            g2.setPaint(gp);
            g2.fillRect(0, 0, SCREEN_W, SCREEN_H);

            // Top logo block
            g2.setFont(logoFont);
            drawGlowText(g2, GAME_TITLE, 70, 170);

            g2.setFont(subLogoFont);
            g2.setColor(new Color(200, 200, 220));
            g2.drawString(APP_TITLE, 74, 195);

            // Left menu plate
            g2.setColor(new Color(20, 20, 40, 220));
            g2.fillRoundRect(60, 240, 360, 250, 18, 18);

            // Determine which list to draw
            String header;
            String[] items;
            int selected;

            if (scene == Scene.MAIN_MENU) {
                header = "MAIN MENU";
                items = mainItems;
                selected = mainIndex;
            } else if (scene == Scene.ONLINE_MENU) {
                header = "ONLINE";
                items = onlineItems;
                selected = onlineIndex;
            } else if (scene == Scene.JOIN_BROWSER) {
                header = "JOIN (LAN)";
                items = null;
                selected = joinIndex;
            } else if (scene == Scene.OPTIONS) {
                header = "OPTIONS";
                items = new String[]{"(demo) No options yet", "Press ESC to go back"};
                selected = 0;
            } else {
                header = "LOBBY";
                items = null;
                selected = 0;
            }

            g2.setFont(menuFont);
            g2.setColor(new Color(220, 220, 235));
            g2.drawString(header, 84, 278);

            g2.setFont(menuFont);

            if (scene == Scene.JOIN_BROWSER) {
                drawJoinBrowser(g2);
                drawFooterHints(g2);
                return;
            }

            if (scene == Scene.LOBBY) {
                drawLobby(g2);
                drawFooterHints(g2);
                return;
            }

            // Draw menu items
            int x = 96;
            int y = 320;
            int lineH = 44;

            if (items != null) {
                for (int i = 0; i < items.length; i++) {
                    boolean hot = (i == selected) && (scene == Scene.MAIN_MENU || scene == Scene.ONLINE_MENU);
                    if (hot) {
                        // highlight bar
                        g2.setColor(new Color(255, 255, 255, 18));
                        g2.fillRoundRect(80, y - 28, 320, 38, 12, 12);

                        // cursor
                        drawCursor(g2, 72, y - 18);
                        g2.setColor(new Color(255, 255, 255));
                    } else {
                        g2.setColor(new Color(210, 210, 230));
                    }
                    g2.drawString(items[i], x, y);
                    y += lineH;
                }
            }

            // Right status panel
            drawStatusPanel(g2);

            drawFooterHints(g2);
        }

        void drawCursor(Graphics2D g2, int x, int y) {
            int size = 14;
            Polygon p = new Polygon();
            p.addPoint(x, y);
            p.addPoint(x + size, y + size / 2);
            p.addPoint(x, y + size);
            g2.setColor(new Color(255, 220, 120));
            g2.fillPolygon(p);
        }

        void drawStatusPanel(Graphics2D g2) {
            g2.setColor(new Color(20, 20, 40, 200));
            g2.fillRoundRect(450, 240, 300, 250, 18, 18);

            g2.setFont(menuFont);
            g2.setColor(new Color(220, 220, 235));
            g2.drawString("STATUS", 474, 278);

            g2.setFont(smallFont);
            g2.setColor(new Color(200, 200, 220));

            String netLine;
            if (server != null && server.running) {
                netLine = "Hosting LAN server on port " + SERVER_PORT + " (" + server.clientCount() + " clients)";
            } else if (client != null && client.serverInfo != null) {
                netLine = "Connected to " + client.serverInfo.serverName + " - " + client.serverInfo.version;
            } else {
                netLine = "Not connected";
            }

            g2.drawString(netLine, 474, 312);

            if (client != null && client.bundle != null) {
                g2.drawString("Downloaded bundle: " + client.bundle.gameId, 474, 336);
                g2.drawString("Levels: " + String.join(", ", client.bundle.levels), 474, 356);
            }

            g2.drawString("Player: " + player.name, 474, 392);
            g2.drawString("Use ARROWS + ENTER. ESC = Back", 474, 416);
        }

        void drawLobby(Graphics2D g2) {
            g2.setColor(new Color(20, 20, 40, 220));
            g2.fillRoundRect(60, 240, 690, 250, 18, 18);

            g2.setFont(menuFont);
            g2.setColor(new Color(220, 220, 235));
            g2.drawString("LOBBY", 84, 278);

            g2.setFont(smallFont);
            g2.setColor(new Color(200, 200, 220));

            int y = 320;
            if (server != null && server.running) {
                g2.drawString("Mode: HOST", 96, y); y += 22;
                g2.drawString("LAN Beacon: ON (UDP " + DISCOVERY_PORT + ")", 96, y); y += 22;
                g2.drawString("TCP Server:  " + localAddress() + ":" + SERVER_PORT, 96, y); y += 22;
                g2.drawString("Clients:     " + server.clientCount(), 96, y); y += 22;
            } else if (client != null && (client.serverInfo != null || client.bundle != null)) {
                g2.drawString("Mode: JOIN", 96, y); y += 22;
                if (client.serverInfo != null) {
                    g2.drawString("Server: " + client.serverInfo.serverName + " - " + client.serverInfo.version, 96, y); y += 22;
                }
                if (client.bundle != null) {
                    g2.drawString("Bundle: " + client.bundle.gameId + " | Levels: " + String.join(", ", client.bundle.levels), 96, y); y += 22;
                    g2.drawString("MOTD: " + client.bundle.motd, 96, y); y += 22;
                }
            } else {
                g2.drawString("Mode: LOCAL", 96, y); y += 22;
                g2.drawString("No networking active.", 96, y); y += 22;
            }

            y += 10;
            g2.setFont(menuFont);
            g2.setColor(Color.WHITE);
            g2.drawString("PRESS ENTER TO START", 96, y + 40);
        }

        void drawJoinBrowser(Graphics2D g2) {
            List<ServerListing> list = discovery.snapshot();

            g2.setColor(new Color(20, 20, 40, 220));
            g2.fillRoundRect(60, 240, 690, 250, 18, 18);

            g2.setFont(menuFont);
            g2.setColor(new Color(220, 220, 235));
            g2.drawString("JOIN (LAN)", 84, 278);

            g2.setFont(smallFont);
            g2.setColor(new Color(200, 200, 220));
            g2.drawString("Listening on UDP " + DISCOVERY_PORT + " for hosts broadcasting '" + NET_MAGIC + "|...'", 84, 302);

            int x = 96;
            int y = 338;
            int lineH = 26;

            if (list.isEmpty()) {
                g2.drawString("No hosts found yet...", x, y);
                return;
            }

            joinIndex = Math.max(0, Math.min(joinIndex, list.size() - 1));

            for (int i = 0; i < list.size(); i++) {
                boolean hot = i == joinIndex;
                if (hot) {
                    g2.setColor(new Color(255, 255, 255, 18));
                    g2.fillRoundRect(80, y - 18, 640, 24, 10, 10);
                    drawCursor(g2, 72, y - 16);
                    g2.setColor(Color.WHITE);
                } else {
                    g2.setColor(new Color(210, 210, 230));
                }
                g2.drawString(list.get(i).displayLine(), x, y);
                y += lineH;
            }
        }

        void drawFooterHints(Graphics2D g2) {
            g2.setFont(smallFont);
            g2.setColor(new Color(200, 200, 220));
            g2.drawString("ARROWS: move   ENTER: select/start   ESC: back/quit", 60, SCREEN_H - 20);
        }

        void drawGlowText(Graphics2D g2, String text, int x, int y) {
            // Fake glow by drawing text multiple times
            g2.setFont(logoFont);
            g2.setColor(new Color(255, 240, 160, 90));
            for (int dx = -2; dx <= 2; dx++) {
                for (int dy = -2; dy <= 2; dy++) {
                    if (dx == 0 && dy == 0) continue;
                    g2.drawString(text, x + dx, y + dy);
                }
            }
            g2.setColor(Color.WHITE);
            g2.drawString(text, x, y);
        }

        /* ---------------- GAME ---------------- */
        void drawGame(Graphics2D g2) {
            // Sky
            g2.setColor(new Color(135, 206, 235));
            g2.fillRect(0, 0, SCREEN_W, SCREEN_H);

            // Ground
            g2.setColor(new Color(80, 170, 70));
            g2.fillRect(0, SCREEN_H - 80, SCREEN_W, 80);

            // Player block
            g2.setColor(new Color(30, 70, 220));
            g2.fillRoundRect((int) player.x, (int) player.y, 32, 32, 8, 8);

            // HUD
            hud.render(g2, player);

            // Mini help
            g2.setFont(smallFont);
            g2.setColor(new Color(0, 0, 0, 140));
            g2.fillRoundRect(12, SCREEN_H - 44, 420, 28, 10, 10);
            g2.setColor(Color.WHITE);
            g2.drawString("Move: ARROWS   ESC: back to lobby", 22, SCREEN_H - 25);
        }

        static float clamp(float v, float lo, float hi) {
            return Math.max(lo, Math.min(hi, v));
        }

        static String localAddress() {
            try {
                // Best-effort pick for LAN IP
                try (DatagramSocket s = new DatagramSocket()) {
                    s.connect(InetAddress.getByName("8.8.8.8"), 80);
                    return s.getLocalAddress().getHostAddress();
                }
            } catch (Exception ignored) {
                return "127.0.0.1";
            }
        }
    }

    /* ===================== MAIN ===================== */
    public static void main(String[] args) throws Exception {
        RomAdapter rom = new RomAdapter();
        String gameId = "SamsoftMarioLive";
        rom.loadGameData(gameId);

        SwingUtilities.invokeLater(() -> {
            JFrame frame = new JFrame(APP_TITLE);
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setResizable(false);

            frame.add(new GamePanel(rom, gameId));
            frame.pack();
            frame.setLocationRelativeTo(null);
            frame.setVisible(true);
        });
    }
}
