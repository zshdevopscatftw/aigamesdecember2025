import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Map;
import java.util.HashMap;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import javax.swing.JFrame;
import javax.swing.JPanel;

/* ============================================================
   SML — SUPER MARIO BROS. LIVE!
   Single-file Java engine
   Java 17+
   ============================================================ */

public class SML {

    /* ===================== CONFIG ===================== */
    static final int SCREEN_W = 800;
    static final int SCREEN_H = 600;
    static final int SERVER_PORT = 7777;
    static final int DISCOVERY_PORT = 7778;

    /* ===================== GAME STATE ===================== */
    enum GameState {
        MENU,
        PLAYING
    }

    static GameState currentState = GameState.MENU;

    /* ===================== NETWORK ===================== */
    enum PacketType {
        HANDSHAKE,
        HANDSHAKE_ACK,
        PLAYER_UPDATE,
        CHAT,
        ZONE_CHANGE,
        ENTITY_UPDATE,
        HEARTBEAT,
        DISCOVERY_BEACON
    }

    static record Packet(PacketType type, Object payload)
            implements Serializable {}

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
        float y = 100;
        Stats stats = new Stats();

        Player(String name) {
            this.name = name;
        }
    }

    enum ZoneType {
        OVERWORLD, DUNGEON, TOWN
    }

    static class Zone {
        String id;
        ZoneType type;
        Set<String> players = ConcurrentHashMap.newKeySet();

        Zone(String id, ZoneType type) {
            this.id = id;
            this.type = type;
        }
    }

    /* ===================== ROM ADAPTER ===================== */
    static class RomAdapter {
        Map<String, java.util.List<String>> extractedLevels = new HashMap<>();

        void loadGameData(String gameId) {
            System.out.println("[ROM] Loading metadata for " + gameId);
            extractedLevels.put(
                gameId,
                java.util.List.of("Town", "Dungeon", "Castle")
            );
        }
    }

    /* ===================== SERVER ===================== */
    static class DownloadPlayServer {
        ServerSocket server;
        Map<String, ClientHandler> clients = new ConcurrentHashMap<>();
        boolean running = true;

        void start() throws IOException {
            server = new ServerSocket(SERVER_PORT);
            new Thread(this::acceptLoop).start();
            new Thread(this::broadcastBeacon).start();
            System.out.println("[SERVER] Online at port " + SERVER_PORT);
        }

        void acceptLoop() {
            while (running) {
                try {
                    Socket socket = server.accept();
                    ClientHandler handler = new ClientHandler(socket);
                    clients.put(socket.getRemoteSocketAddress().toString(), handler);
                    new Thread(handler).start();
                } catch (IOException ignored) {}
            }
        }

        void broadcastBeacon() {
            try (DatagramSocket socket = new DatagramSocket()) {
                socket.setBroadcast(true);
                while (running) {
                    String msg = "SML|" + clients.size();
                    byte[] data = msg.getBytes();
                    DatagramPacket packet = new DatagramPacket(
                        data,
                        data.length,
                        InetAddress.getByName("255.255.255.255"),
                        DISCOVERY_PORT
                    );
                    socket.send(packet);
                    Thread.sleep(1000);
                }
            } catch (Exception ignored) {}
        }

        class ClientHandler implements Runnable {
            Socket socket;
            ObjectInputStream in;
            ObjectOutputStream out;

            ClientHandler(Socket socket) {
                this.socket = socket;
            }

            public void run() {
                try {
                    out = new ObjectOutputStream(socket.getOutputStream());
                    in = new ObjectInputStream(socket.getInputStream());
                    while (running) {
                        Packet packet = (Packet) in.readObject();
                        handle(packet);
                    }
                } catch (Exception e) {
                    clients.remove(socket.getRemoteSocketAddress().toString());
                }
            }

            void handle(Packet packet) throws IOException {
                if (packet.type == PacketType.HANDSHAKE) {
                    out.writeObject(
                        new Packet(PacketType.HANDSHAKE_ACK, "OK")
                    );
                } else {
                    broadcast(packet);
                }
            }
        }

        void broadcast(Packet packet) throws IOException {
            for (ClientHandler c : clients.values()) {
                c.out.writeObject(packet);
            }
        }
    }

    /* ===================== HUD ===================== */
    static class GameHUD {
        void render(Graphics2D g, Player p) {
            g.setColor(new Color(30, 30, 90));
            g.fillRect(0, 0, SCREEN_W, 50);

            g.setColor(Color.RED);
            g.fillRect(20, 15, p.stats.hp * 2, 20);

            g.setColor(Color.WHITE);
            g.drawString("HP: " + p.stats.hp, 20, 45);
        }
    }

    /* ===================== GAME PANEL ===================== */
    static class GamePanel extends JPanel implements Runnable {
        Player player = new Player("Player");
        GameHUD hud = new GameHUD();
        boolean running = true;

        Font titleFont = new Font("SansSerif", Font.BOLD, 48);
        Font menuFont = new Font("SansSerif", Font.BOLD, 20);

        GamePanel() {
            setPreferredSize(new Dimension(SCREEN_W, SCREEN_H));
            setFocusable(true);

            addKeyListener(new KeyAdapter() {
                public void keyPressed(KeyEvent e) {
                    if (currentState == GameState.MENU) {
                        if (e.getKeyCode() == KeyEvent.VK_ENTER) {
                            currentState = GameState.PLAYING;
                        }
                        if (e.getKeyCode() == KeyEvent.VK_ESCAPE) {
                            System.exit(0);
                        }
                        return;
                    }

                    switch (e.getKeyCode()) {
                        case KeyEvent.VK_LEFT -> player.x -= 5;
                        case KeyEvent.VK_RIGHT -> player.x += 5;
                        case KeyEvent.VK_UP -> player.y -= 5;
                        case KeyEvent.VK_DOWN -> player.y += 5;
                    }
                }
            });

            new Thread(this).start();
        }

        public void run() {
            while (running) {
                repaint();
                try { Thread.sleep(16); } catch (InterruptedException ignored) {}
            }
        }

        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            Graphics2D g2 = (Graphics2D) g;

            if (currentState == GameState.MENU) {
                drawMenu(g2);
            } else {
                drawGame(g2);
            }
        }

        void drawMenu(Graphics2D g2) {
            g2.setColor(Color.BLACK);
            g2.fillRect(0, 0, SCREEN_W, SCREEN_H);

            g2.setFont(titleFont);
            g2.setColor(Color.WHITE);
            g2.drawString(
                "SUPER MARIO BROS. LIVE!",
                80,
                200
            );

            g2.setFont(menuFont);
            g2.drawString("PRESS ENTER TO START", 270, 300);
            g2.drawString("PRESS ESC TO QUIT", 290, 340);
        }

        void drawGame(Graphics2D g2) {
            g2.setColor(new Color(135, 206, 235));
            g2.fillRect(0, 0, SCREEN_W, SCREEN_H);

            g2.setColor(Color.BLUE);
            g2.fillRect((int)player.x, (int)player.y, 32, 32);

            hud.render(g2, player);
        }
    }

    /* ===================== MAIN ===================== */
    public static void main(String[] args) throws Exception {
        RomAdapter rom = new RomAdapter();
        rom.loadGameData("SuperMarioRPG");

        DownloadPlayServer server = new DownloadPlayServer();
        server.start();

        JFrame frame = new JFrame("Super Mario Bros. Live!");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setResizable(false);
        frame.add(new GamePanel());
        frame.pack();
        frame.setLocationRelativeTo(null);
        frame.setVisible(true);
    }
}
