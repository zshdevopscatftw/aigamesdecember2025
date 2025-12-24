/*
 * ╔═══════════════════════════════════════════════════════════════════════════════╗
 * ║   S!MARIO RPG — SAMSOFT MARIO RPG                                             ║
 * ║   Super Mario RPG (SNES) Style Engine                                         ║
 * ║   Auto Online = Auto Join or Auto Host (DS Download Play Style)               ║
 * ║   Team Flames / Samsoft 2025                                                  ║
 * ╚═══════════════════════════════════════════════════════════════════════════════╝
 *
 * Character Classes: Human, Koopa, Toad, Goomba, Yoshi
 * 
 * Compile: javac S!MarioRPG.java
 * Run: java SMarioRPG
 */

import java.awt.*;
import java.awt.event.*;
import java.awt.geom.*;
import java.awt.image.*;
import java.io.*;
import java.net.*;
import java.util.*;
import java.util.List;
import java.util.concurrent.*;
import javax.swing.*;

public class SMarioRPG {

    // ============================================================
    // CONFIGURATION
    // ============================================================
    static final int W = 900, H = 700;
    static final int TCP_PORT = 7777;
    static final int UDP_PORT = 7778;
    static final String MAGIC = "SAMSOFT_RPG";
    static final String TITLE = "S!MARIO RPG — Samsoft Edition";
    static final int FPS = 60;

    // SMRPG Color Palette
    static final Color SKY_TOP = new Color(100, 150, 220);
    static final Color SKY_BOTTOM = new Color(180, 210, 255);
    static final Color GRASS_GREEN = new Color(80, 160, 80);
    static final Color GRASS_DARK = new Color(50, 120, 50);
    static final Color STAR_YELLOW = new Color(255, 230, 0);
    static final Color COIN_GOLD = new Color(255, 200, 50);
    static final Color UI_BLUE = new Color(0, 60, 140);
    static final Color UI_BORDER = new Color(255, 200, 100);
    static final Color HP_RED = new Color(220, 50, 50);
    static final Color HP_GREEN = new Color(50, 200, 50);
    static final Color MP_BLUE = new Color(50, 100, 220);

    // ============================================================
    // CHARACTER CLASSES ENUM
    // ============================================================
    enum CharacterClass {
        HUMAN("Human", new Color(255, 200, 150), 100, 30, 12, 8, "Balanced fighter with sword skills"),
        KOOPA("Koopa", new Color(50, 180, 50), 120, 20, 10, 12, "Tough shell defense, spinning attacks"),
        TOAD("Toad", new Color(255, 100, 100), 80, 50, 8, 6, "Healing magic specialist"),
        GOOMBA("Goomba", new Color(180, 120, 80), 90, 25, 14, 5, "High attack, low defense"),
        YOSHI("Yoshi", new Color(100, 220, 100), 110, 35, 11, 9, "Egg attacks, flutter jump");

        final String name;
        final Color color;
        final int baseHP, baseMP, baseATK, baseDEF;
        final String description;

        CharacterClass(String name, Color color, int hp, int mp, int atk, int def, String desc) {
            this.name = name;
            this.color = color;
            this.baseHP = hp;
            this.baseMP = mp;
            this.baseATK = atk;
            this.baseDEF = def;
            this.description = desc;
        }
    }

    // ============================================================
    // PLAYER STATE
    // ============================================================
    static class PlayerState implements Serializable {
        static final long serialVersionUID = 1L;
        String name;
        CharacterClass charClass;
        float x, y;
        int facing = 1;
        int animFrame = 0;
        int hp, maxHP;
        int mp, maxMP;
        int atk, def;
        int level = 1;
        int exp = 0;
        int coins = 0;
        boolean jumping = false;
        float jumpVel = 0;

        PlayerState(String name, CharacterClass charClass, float x, float y) {
            this.name = name;
            this.charClass = charClass;
            this.x = x;
            this.y = y;
            this.maxHP = charClass.baseHP;
            this.hp = maxHP;
            this.maxMP = charClass.baseMP;
            this.mp = maxMP;
            this.atk = charClass.baseATK;
            this.def = charClass.baseDEF;
        }
    }

    // ============================================================
    // NETWORK - AUTO ONLINE HOST
    // ============================================================
    static class AutoHost {
        ServerSocket server;
        DatagramSocket beacon;
        volatile boolean running = true;
        Map<Socket, ObjectOutputStream> clients = new ConcurrentHashMap<>();

        void start() throws IOException {
            server = new ServerSocket(TCP_PORT);
            server.setReuseAddress(true);
            server.setSoTimeout(500);

            new Thread(this::acceptLoop, "host-accept").start();
            new Thread(this::beaconLoop, "host-beacon").start();
            System.out.println("[HOST] Started on port " + TCP_PORT);
        }

        void acceptLoop() {
            while (running) {
                try {
                    Socket s = server.accept();
                    ObjectOutputStream out = new ObjectOutputStream(s.getOutputStream());
                    out.flush();
                    clients.put(s, out);
                    new Thread(() -> clientLoop(s), "host-client").start();
                } catch (SocketTimeoutException ignored) {
                } catch (Exception e) {
                    if (running) e.printStackTrace();
                }
            }
        }

        void clientLoop(Socket s) {
            try (ObjectInputStream in = new ObjectInputStream(s.getInputStream())) {
                while (running) {
                    Object o = in.readObject();
                    if (o instanceof PlayerState) {
                        broadcast((PlayerState) o, s);
                    }
                }
            } catch (Exception ignored) {
            }
            clients.remove(s);
        }

        void broadcast(PlayerState p, Socket exclude) {
            clients.forEach((sock, out) -> {
                if (sock != exclude) {
                    try {
                        synchronized (out) {
                            out.writeObject(p);
                            out.reset();
                            out.flush();
                        }
                    } catch (Exception ignored) {
                    }
                }
            });
        }

        void beaconLoop() {
            try {
                beacon = new DatagramSocket();
                beacon.setBroadcast(true);
                while (running) {
                    String msg = MAGIC + "|" + TCP_PORT;
                    byte[] b = msg.getBytes();
                    beacon.send(new DatagramPacket(b, b.length,
                            InetAddress.getByName("255.255.255.255"), UDP_PORT));
                    Thread.sleep(700);
                }
            } catch (Exception ignored) {
            }
        }

        void stop() {
            running = false;
            try { if (server != null) server.close(); } catch (Exception ignored) {}
            try { if (beacon != null) beacon.close(); } catch (Exception ignored) {}
        }
    }

    // ============================================================
    // NETWORK - AUTO ONLINE CLIENT
    // ============================================================
    static class AutoClient {
        Socket socket;
        ObjectOutputStream out;
        ObjectInputStream in;
        volatile boolean connected = false;
        ConcurrentLinkedQueue<PlayerState> recvQueue = new ConcurrentLinkedQueue<>();

        boolean connect(InetAddress addr) {
            try {
                socket = new Socket(addr, TCP_PORT);
                out = new ObjectOutputStream(socket.getOutputStream());
                out.flush();
                in = new ObjectInputStream(socket.getInputStream());
                connected = true;
                new Thread(this::readLoop, "client-read").start();
                System.out.println("[CLIENT] Connected to " + addr.getHostAddress());
                return true;
            } catch (Exception e) {
                return false;
            }
        }

        void readLoop() {
            try {
                while (connected) {
                    Object o = in.readObject();
                    if (o instanceof PlayerState) {
                        recvQueue.add((PlayerState) o);
                    }
                }
            } catch (Exception ignored) {
            }
            connected = false;
        }

        void send(PlayerState p) {
            if (connected && out != null) {
                try {
                    synchronized (out) {
                        out.writeObject(p);
                        out.reset();
                        out.flush();
                    }
                } catch (Exception ignored) {
                }
            }
        }

        List<PlayerState> getStates() {
            List<PlayerState> list = new ArrayList<>();
            PlayerState p;
            while ((p = recvQueue.poll()) != null) {
                list.add(p);
            }
            return list;
        }
    }

    // ============================================================
    // AUTO ONLINE DISCOVERY
    // ============================================================
    static class AutoOnline {
        AutoHost host;
        AutoClient client;
        String mode = "";

        void discover() {
            // Try to find existing host
            try {
                DatagramSocket s = new DatagramSocket(null);
                s.setReuseAddress(true);
                s.bind(new InetSocketAddress(UDP_PORT));
                s.setSoTimeout(1000);

                byte[] buf = new byte[128];
                DatagramPacket p = new DatagramPacket(buf, buf.length);
                s.receive(p);
                s.close();

                String msg = new String(p.getData(), 0, p.getLength());
                if (msg.startsWith(MAGIC)) {
                    // Found host, connect as client
                    client = new AutoClient();
                    if (client.connect(p.getAddress())) {
                        mode = "client";
                        return;
                    }
                }
            } catch (Exception ignored) {
            }

            // No host found, become host
            try {
                host = new AutoHost();
                host.start();
                mode = "host";

                // Connect to self
                Thread.sleep(100);
                client = new AutoClient();
                client.connect(InetAddress.getLocalHost());
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        void stop() {
            if (host != null) host.stop();
        }
    }

    // ============================================================
    // SMRPG SPRITE RENDERER
    // ============================================================
    static class SMRPGSprites {

        static void drawHuman(Graphics2D g, int x, int y, int facing, int frame, float scale) {
            int s = (int) scale;
            
            // Shadow
            g.setColor(new Color(0, 0, 0, 80));
            g.fillOval(x - 12 * s, y + 25 * s, 24 * s, 8 * s);

            // Legs
            int legOff = (int) (Math.sin(frame * 0.5) * 3 * s);
            g.setColor(new Color(100, 80, 60));
            g.fillRect(x - 6 * s - legOff, y + 12 * s, 5 * s, 14 * s);
            g.fillRect(x + 1 * s + legOff, y + 12 * s, 5 * s, 14 * s);

            // Boots
            g.setColor(new Color(80, 50, 30));
            g.fillOval(x - 8 * s - legOff, y + 22 * s, 8 * s, 6 * s);
            g.fillOval(x + legOff, y + 22 * s, 8 * s, 6 * s);

            // Body (tunic)
            g.setColor(new Color(100, 150, 200));
            g.fillOval(x - 10 * s, y - 2 * s, 20 * s, 18 * s);

            // Belt
            g.setColor(new Color(139, 90, 43));
            g.fillRect(x - 10 * s, y + 8 * s, 20 * s, 4 * s);
            g.setColor(COIN_GOLD);
            g.fillOval(x - 3 * s, y + 7 * s, 6 * s, 6 * s);

            // Head
            g.setColor(new Color(255, 200, 150));
            g.fillOval(x - 8 * s, y - 18 * s, 16 * s, 18 * s);

            // Hair
            g.setColor(new Color(139, 90, 43));
            g.fillArc(x - 9 * s, y - 20 * s, 18 * s, 14 * s, 0, 180);

            // Eyes
            g.setColor(Color.WHITE);
            g.fillOval(x - 5 * s, y - 12 * s, 4 * s, 5 * s);
            g.fillOval(x + 1 * s, y - 12 * s, 4 * s, 5 * s);
            g.setColor(Color.BLACK);
            g.fillOval(x - 4 * s + facing, y - 11 * s, 2 * s, 3 * s);
            g.fillOval(x + 2 * s + facing, y - 11 * s, 2 * s, 3 * s);

            // Sword
            g.setColor(new Color(180, 180, 200));
            g.fillRect(x + 10 * s * facing, y - 5 * s, 4 * s, 20 * s);
            g.setColor(COIN_GOLD);
            g.fillRect(x + 8 * s * facing, y + 10 * s, 8 * s, 4 * s);

            // Gloves
            g.setColor(new Color(200, 180, 150));
            g.fillOval(x - 14 * s, y + 2 * s, 6 * s, 6 * s);
            g.fillOval(x + 8 * s, y + 2 * s, 6 * s, 6 * s);
        }

        static void drawKoopa(Graphics2D g, int x, int y, int facing, int frame, float scale) {
            int s = (int) scale;

            // Shadow
            g.setColor(new Color(0, 0, 0, 80));
            g.fillOval(x - 14 * s, y + 22 * s, 28 * s, 10 * s);

            // Feet
            int legOff = (int) (Math.sin(frame * 0.5) * 2 * s);
            g.setColor(new Color(255, 200, 100));
            g.fillOval(x - 10 * s - legOff, y + 18 * s, 10 * s, 8 * s);
            g.fillOval(x + legOff, y + 18 * s, 10 * s, 8 * s);

            // Shell
            g.setColor(new Color(50, 180, 50));
            g.fillOval(x - 14 * s, y - 5 * s, 28 * s, 28 * s);

            // Shell pattern
            g.setColor(new Color(30, 140, 30));
            g.fillOval(x - 8 * s, y, 16 * s, 16 * s);
            g.setColor(new Color(255, 220, 150));
            g.fillOval(x - 5 * s, y + 3 * s, 10 * s, 10 * s);

            // Head
            g.setColor(new Color(255, 220, 150));
            g.fillOval(x - 8 * s, y - 20 * s, 16 * s, 18 * s);

            // Beak
            g.setColor(new Color(255, 200, 100));
            g.fillOval(x + 2 * s * facing, y - 10 * s, 10 * s, 6 * s);

            // Eyes
            g.setColor(Color.WHITE);
            g.fillOval(x - 5 * s, y - 16 * s, 5 * s, 6 * s);
            g.fillOval(x, y - 16 * s, 5 * s, 6 * s);
            g.setColor(Color.BLACK);
            g.fillOval(x - 3 * s + facing, y - 14 * s, 2 * s, 3 * s);
            g.fillOval(x + 2 * s + facing, y - 14 * s, 2 * s, 3 * s);

            // Arms
            g.setColor(new Color(255, 220, 150));
            g.fillOval(x - 16 * s, y, 8 * s, 8 * s);
            g.fillOval(x + 8 * s, y, 8 * s, 8 * s);
        }

        static void drawToad(Graphics2D g, int x, int y, int facing, int frame, float scale) {
            int s = (int) scale;

            // Shadow
            g.setColor(new Color(0, 0, 0, 80));
            g.fillOval(x - 10 * s, y + 20 * s, 20 * s, 8 * s);

            // Feet
            int legOff = (int) (Math.sin(frame * 0.5) * 2 * s);
            g.setColor(new Color(200, 150, 100));
            g.fillOval(x - 8 * s - legOff, y + 16 * s, 8 * s, 6 * s);
            g.fillOval(x + legOff, y + 16 * s, 8 * s, 6 * s);

            // Body (vest)
            g.setColor(new Color(100, 80, 200));
            g.fillOval(x - 8 * s, y, 16 * s, 18 * s);

            // Vest details
            g.setColor(COIN_GOLD);
            g.fillOval(x - 2 * s, y + 3 * s, 4 * s, 4 * s);

            // Head (large mushroom cap)
            g.setColor(Color.WHITE);
            g.fillOval(x - 14 * s, y - 24 * s, 28 * s, 24 * s);

            // Mushroom spots
            g.setColor(new Color(255, 80, 80));
            g.fillOval(x - 10 * s, y - 22 * s, 8 * s, 8 * s);
            g.fillOval(x + 2 * s, y - 22 * s, 8 * s, 8 * s);
            g.fillOval(x - 4 * s, y - 16 * s, 6 * s, 6 * s);

            // Face
            g.setColor(new Color(255, 220, 200));
            g.fillOval(x - 8 * s, y - 12 * s, 16 * s, 14 * s);

            // Eyes
            g.setColor(Color.BLACK);
            g.fillOval(x - 5 * s, y - 8 * s, 4 * s, 5 * s);
            g.fillOval(x + 1 * s, y - 8 * s, 4 * s, 5 * s);

            // Cheeks
            g.setColor(new Color(255, 180, 180));
            g.fillOval(x - 8 * s, y - 4 * s, 4 * s, 3 * s);
            g.fillOval(x + 4 * s, y - 4 * s, 4 * s, 3 * s);

            // Hands
            g.setColor(Color.WHITE);
            g.fillOval(x - 12 * s, y + 4 * s, 6 * s, 6 * s);
            g.fillOval(x + 6 * s, y + 4 * s, 6 * s, 6 * s);
        }

        static void drawGoomba(Graphics2D g, int x, int y, int facing, int frame, float scale) {
            int s = (int) scale;

            // Shadow
            g.setColor(new Color(0, 0, 0, 80));
            g.fillOval(x - 12 * s, y + 18 * s, 24 * s, 8 * s);

            // Feet
            int legOff = (int) (Math.sin(frame * 0.5) * 3 * s);
            g.setColor(new Color(80, 50, 30));
            g.fillOval(x - 10 * s - legOff, y + 14 * s, 10 * s, 8 * s);
            g.fillOval(x + legOff, y + 14 * s, 10 * s, 8 * s);

            // Body
            g.setColor(new Color(180, 120, 80));
            g.fillOval(x - 12 * s, y - 8 * s, 24 * s, 26 * s);

            // Face area (lighter)
            g.setColor(new Color(255, 220, 180));
            g.fillOval(x - 10 * s, y - 4 * s, 20 * s, 18 * s);

            // Eyebrows (angry)
            g.setColor(Color.BLACK);
            g.setStroke(new BasicStroke(2 * s));
            g.drawLine(x - 8 * s, y - 2 * s, x - 2 * s, y - 5 * s);
            g.drawLine(x + 8 * s, y - 2 * s, x + 2 * s, y - 5 * s);

            // Eyes
            g.setColor(Color.WHITE);
            g.fillOval(x - 7 * s, y - 2 * s, 6 * s, 8 * s);
            g.fillOval(x + 1 * s, y - 2 * s, 6 * s, 8 * s);
            g.setColor(Color.BLACK);
            g.fillOval(x - 5 * s + facing, y, 3 * s, 5 * s);
            g.fillOval(x + 2 * s + facing, y, 3 * s, 5 * s);

            // Fangs
            g.setColor(Color.WHITE);
            int[] fangX = {x - 4 * s, x - 2 * s, x - 3 * s};
            int[] fangY = {y + 8 * s, y + 8 * s, y + 12 * s};
            g.fillPolygon(fangX, fangY, 3);
            int[] fang2X = {x + 2 * s, x + 4 * s, x + 3 * s};
            g.fillPolygon(fang2X, fangY, 3);
        }

        static void drawYoshi(Graphics2D g, int x, int y, int facing, int frame, float scale) {
            int s = (int) scale;

            // Shadow
            g.setColor(new Color(0, 0, 0, 80));
            g.fillOval(x - 14 * s, y + 22 * s, 28 * s, 10 * s);

            // Tail
            g.setColor(new Color(100, 220, 100));
            int[] tailX = {x - 12 * s * facing, x - 20 * s * facing, x - 16 * s * facing};
            int[] tailY = {y + 10 * s, y + 15 * s, y + 20 * s};
            g.fillPolygon(tailX, tailY, 3);

            // Feet (orange boots)
            int legOff = (int) (Math.sin(frame * 0.5) * 3 * s);
            g.setColor(new Color(255, 150, 50));
            g.fillOval(x - 10 * s - legOff, y + 16 * s, 10 * s, 8 * s);
            g.fillOval(x + legOff, y + 16 * s, 10 * s, 8 * s);

            // Body
            g.setColor(new Color(100, 220, 100));
            g.fillOval(x - 12 * s, y - 2 * s, 24 * s, 22 * s);

            // Belly (white)
            g.setColor(Color.WHITE);
            g.fillOval(x - 8 * s, y + 2 * s, 16 * s, 14 * s);

            // Shell (red saddle)
            g.setColor(new Color(255, 80, 80));
            g.fillOval(x - 8 * s, y - 4 * s, 16 * s, 10 * s);

            // Head
            g.setColor(new Color(100, 220, 100));
            g.fillOval(x - 10 * s, y - 26 * s, 20 * s, 26 * s);

            // Nose/snout
            g.fillOval(x + 4 * s * facing, y - 18 * s, 14 * s, 10 * s);

            // Nostril
            g.setColor(new Color(80, 180, 80));
            g.fillOval(x + 10 * s * facing, y - 16 * s, 3 * s, 3 * s);

            // Eyes
            g.setColor(Color.WHITE);
            g.fillOval(x - 6 * s, y - 22 * s, 8 * s, 10 * s);
            g.fillOval(x + facing * 2 * s, y - 22 * s, 8 * s, 10 * s);
            g.setColor(Color.BLACK);
            g.fillOval(x - 3 * s + facing, y - 18 * s, 3 * s, 5 * s);
            g.fillOval(x + 3 * s + facing, y - 18 * s, 3 * s, 5 * s);

            // Cheeks (orange)
            g.setColor(new Color(255, 180, 100));
            g.fillOval(x - 8 * s, y - 12 * s, 4 * s, 4 * s);
            g.fillOval(x + 6 * s, y - 12 * s, 4 * s, 4 * s);

            // Arms
            g.setColor(new Color(100, 220, 100));
            g.fillOval(x - 16 * s, y + 2 * s, 8 * s, 8 * s);
            g.fillOval(x + 8 * s, y + 2 * s, 8 * s, 8 * s);
        }

        static void drawCharacter(Graphics2D g, int x, int y, CharacterClass c, int facing, int frame, float scale) {
            switch (c) {
                case HUMAN -> drawHuman(g, x, y, facing, frame, scale);
                case KOOPA -> drawKoopa(g, x, y, facing, frame, scale);
                case TOAD -> drawToad(g, x, y, facing, frame, scale);
                case GOOMBA -> drawGoomba(g, x, y, facing, frame, scale);
                case YOSHI -> drawYoshi(g, x, y, facing, frame, scale);
            }
        }
    }

    // ============================================================
    // SMRPG BACKGROUND
    // ============================================================
    static class SMRPGBackground {
        float[] cloudX = new float[5];
        float[] cloudY = new float[5];
        float[] cloudSpeed = new float[5];
        int[][] groundTiles;
        Random rand = new Random();

        SMRPGBackground() {
            for (int i = 0; i < 5; i++) {
                cloudX[i] = rand.nextFloat() * W;
                cloudY[i] = 50 + rand.nextFloat() * 100;
                cloudSpeed[i] = 0.3f + rand.nextFloat() * 0.3f;
            }
            groundTiles = new int[H / 32 + 1][W / 32 + 1];
            for (int y = 0; y < groundTiles.length; y++) {
                for (int x = 0; x < groundTiles[0].length; x++) {
                    groundTiles[y][x] = rand.nextInt(3);
                }
            }
        }

        void update(float dt) {
            for (int i = 0; i < 5; i++) {
                cloudX[i] += cloudSpeed[i];
                if (cloudX[i] > W + 100) cloudX[i] = -100;
            }
        }

        void draw(Graphics2D g) {
            // Sky gradient
            GradientPaint sky = new GradientPaint(0, 0, SKY_TOP, 0, H, SKY_BOTTOM);
            g.setPaint(sky);
            g.fillRect(0, 0, W, H);

            // Clouds
            g.setColor(Color.WHITE);
            for (int i = 0; i < 5; i++) {
                drawCloud(g, (int) cloudX[i], (int) cloudY[i]);
            }

            // Mountains (background)
            g.setColor(new Color(100, 140, 180));
            int[] mtnX = {0, 150, 300, 450, 600, 750, W, W, 0};
            int[] mtnY = {H - 200, H - 320, H - 250, H - 350, H - 280, H - 300, H - 220, H, H};
            g.fillPolygon(mtnX, mtnY, 9);

            g.setColor(new Color(120, 160, 200));
            int[] mtn2X = {0, 200, 400, 600, 800, W, W, 0};
            int[] mtn2Y = {H - 180, H - 280, H - 200, H - 300, H - 220, H - 200, H, H};
            g.fillPolygon(mtn2X, mtn2Y, 8);

            // Ground
            g.setColor(GRASS_GREEN);
            g.fillRect(0, H - 120, W, 120);

            // Ground pattern
            g.setColor(GRASS_DARK);
            for (int x = 0; x < W; x += 40) {
                g.fillOval(x - 10, H - 125, 30, 15);
            }

            // Isometric tiles (SMRPG style)
            for (int row = 0; row < 3; row++) {
                for (int col = 0; col < 12; col++) {
                    int tx = col * 70 + (row % 2) * 35;
                    int ty = H - 100 + row * 25;
                    drawIsometricTile(g, tx, ty, groundTiles[row][col % groundTiles[0].length]);
                }
            }
        }

        void drawCloud(Graphics2D g, int x, int y) {
            g.setColor(new Color(255, 255, 255, 220));
            g.fillOval(x, y, 60, 30);
            g.fillOval(x + 15, y - 10, 50, 30);
            g.fillOval(x + 35, y, 50, 28);
        }

        void drawIsometricTile(Graphics2D g, int x, int y, int type) {
            int[] px = {x, x + 35, x + 70, x + 35};
            int[] py = {y, y - 15, y, y + 15};

            Color top = switch (type) {
                case 0 -> new Color(120, 200, 120);
                case 1 -> new Color(140, 220, 140);
                default -> new Color(100, 180, 100);
            };

            g.setColor(top);
            g.fillPolygon(px, py, 4);
            g.setColor(new Color(80, 140, 80));
            g.drawPolygon(px, py, 4);
        }
    }

    // ============================================================
    // GAME STATE
    // ============================================================
    static Map<String, PlayerState> players = new ConcurrentHashMap<>();
    static PlayerState me;
    static AutoOnline network;

    // ============================================================
    // GAME PANEL
    // ============================================================
    static class GamePanel extends JPanel implements Runnable {
        Set<Integer> keys = ConcurrentHashMap.newKeySet();
        SMRPGBackground background;
        float animTimer = 0;
        String connectionStatus = "Connecting...";

        GamePanel(String name, CharacterClass charClass) {
            me = new PlayerState(name, charClass, W / 2f, H / 2f);
            background = new SMRPGBackground();

            setPreferredSize(new Dimension(W, H));
            setFocusable(true);
            setDoubleBuffered(true);

            addKeyListener(new KeyAdapter() {
                public void keyPressed(KeyEvent e) { keys.add(e.getKeyCode()); }
                public void keyReleased(KeyEvent e) { keys.remove(e.getKeyCode()); }
            });

            // Start network
            new Thread(() -> {
                network = new AutoOnline();
                network.discover();
                connectionStatus = network.mode.equals("host") ? "★ HOSTING ★" : "● CONNECTED";
            }).start();

            new Thread(this, "game-loop").start();
        }

        public void run() {
            long lastTime = System.nanoTime();
            while (true) {
                long now = System.nanoTime();
                float dt = (now - lastTime) / 1e9f;
                lastTime = now;

                update(dt);
                repaint();

                try { Thread.sleep(16); } catch (Exception ignored) {}
            }
        }

        void update(float dt) {
            // Movement
            float speed = 200 * dt;
            boolean moving = false;

            if (keys.contains(KeyEvent.VK_LEFT) || keys.contains(KeyEvent.VK_A)) {
                me.x -= speed;
                me.facing = -1;
                moving = true;
            }
            if (keys.contains(KeyEvent.VK_RIGHT) || keys.contains(KeyEvent.VK_D)) {
                me.x += speed;
                me.facing = 1;
                moving = true;
            }
            if (keys.contains(KeyEvent.VK_UP) || keys.contains(KeyEvent.VK_W)) {
                me.y -= speed;
                moving = true;
            }
            if (keys.contains(KeyEvent.VK_DOWN) || keys.contains(KeyEvent.VK_S)) {
                me.y += speed;
                moving = true;
            }

            // Jump
            if ((keys.contains(KeyEvent.VK_SPACE) || keys.contains(KeyEvent.VK_Z)) && !me.jumping) {
                me.jumping = true;
                me.jumpVel = -12;
            }

            if (me.jumping) {
                me.y += me.jumpVel;
                me.jumpVel += 0.8f;
                if (me.jumpVel > 0 && me.y >= H / 2f) {
                    me.jumping = false;
                    me.y = H / 2f;
                }
            }

            // Bounds
            me.x = Math.max(40, Math.min(W - 40, me.x));
            me.y = Math.max(60, Math.min(H - 60, me.y));

            // Animation
            if (moving) {
                animTimer += dt * 8;
                me.animFrame = (int) animTimer % 4;
            } else {
                me.animFrame = 0;
            }

            // Network
            players.put(me.name, me);
            if (network != null && network.client != null) {
                network.client.send(me);
                for (PlayerState p : network.client.getStates()) {
                    if (!p.name.equals(me.name)) {
                        players.put(p.name, p);
                    }
                }
            }

            background.update(dt);
        }

        protected void paintComponent(Graphics gg) {
            super.paintComponent(gg);
            Graphics2D g = (Graphics2D) gg;
            g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

            // Background
            background.draw(g);

            // Draw players sorted by Y
            List<PlayerState> sorted = new ArrayList<>(players.values());
            sorted.sort((a, b) -> Float.compare(a.y, b.y));

            for (PlayerState p : sorted) {
                // Draw character
                SMRPGSprites.drawCharacter(g, (int) p.x, (int) p.y, p.charClass, p.facing, p.animFrame, 2);

                // Name tag with class
                String tag = p.name + " (" + p.charClass.name + ")";
                g.setFont(new Font("Arial", Font.BOLD, 14));
                FontMetrics fm = g.getFontMetrics();
                int tw = fm.stringWidth(tag);

                g.setColor(new Color(0, 0, 0, 180));
                g.fillRoundRect((int) p.x - tw / 2 - 5, (int) p.y - 65, tw + 10, 20, 8, 8);
                g.setColor(p.charClass.color);
                g.drawString(tag, (int) p.x - tw / 2, (int) p.y - 50);

                // HP/MP bars
                int barW = 60;
                int barX = (int) p.x - barW / 2;
                int barY = (int) p.y - 42;

                // HP
                g.setColor(new Color(60, 60, 60));
                g.fillRect(barX, barY, barW, 6);
                g.setColor(HP_GREEN);
                g.fillRect(barX, barY, (int) (barW * p.hp / (float) p.maxHP), 6);
                g.setColor(Color.WHITE);
                g.drawRect(barX, barY, barW, 6);

                // MP
                g.setColor(new Color(60, 60, 60));
                g.fillRect(barX, barY + 8, barW, 4);
                g.setColor(MP_BLUE);
                g.fillRect(barX, barY + 8, (int) (barW * p.mp / (float) p.maxMP), 4);
            }

            // UI
            drawUI(g);
        }

        void drawUI(Graphics2D g) {
            // Title bar
            g.setColor(new Color(0, 40, 100, 200));
            g.fillRect(0, 0, W, 50);
            g.setColor(UI_BORDER);
            g.fillRect(0, 48, W, 3);

            // Title
            g.setFont(new Font("Arial", Font.BOLD, 28));
            g.setColor(STAR_YELLOW);
            String title = "S!MARIO RPG";
            FontMetrics fm = g.getFontMetrics();
            g.drawString(title, W / 2 - fm.stringWidth(title) / 2, 35);

            // Version
            g.setFont(new Font("Arial", Font.PLAIN, 12));
            g.setColor(Color.WHITE);
            g.drawString("Samsoft Edition v1.0", 10, 20);

            // Connection status
            g.setColor(connectionStatus.contains("HOST") ? STAR_YELLOW : new Color(100, 255, 100));
            g.setFont(new Font("Arial", Font.BOLD, 14));
            g.drawString(connectionStatus, W - 120, 20);

            // Player count
            g.setColor(Color.WHITE);
            g.drawString("Players: " + players.size(), W - 100, 40);

            // Player info panel (SMRPG style)
            int panelX = 10, panelY = 60;
            int panelW = 180, panelH = 100;

            g.setColor(new Color(0, 60, 140, 220));
            g.fillRoundRect(panelX, panelY, panelW, panelH, 10, 10);
            g.setColor(UI_BORDER);
            g.setStroke(new BasicStroke(3));
            g.drawRoundRect(panelX, panelY, panelW, panelH, 10, 10);

            g.setFont(new Font("Arial", Font.BOLD, 16));
            g.setColor(me.charClass.color);
            g.drawString(me.name, panelX + 10, panelY + 22);

            g.setFont(new Font("Arial", Font.PLAIN, 12));
            g.setColor(Color.WHITE);
            g.drawString("Lv." + me.level + " " + me.charClass.name, panelX + 10, panelY + 40);

            // HP bar
            g.setColor(Color.WHITE);
            g.drawString("HP", panelX + 10, panelY + 58);
            g.setColor(new Color(60, 60, 60));
            g.fillRect(panelX + 35, panelY + 48, 130, 12);
            g.setColor(HP_GREEN);
            g.fillRect(panelX + 35, panelY + 48, (int) (130 * me.hp / (float) me.maxHP), 12);
            g.setColor(Color.WHITE);
            g.drawRect(panelX + 35, panelY + 48, 130, 12);
            g.drawString(me.hp + "/" + me.maxHP, panelX + 80, panelY + 58);

            // MP bar
            g.drawString("MP", panelX + 10, panelY + 78);
            g.setColor(new Color(60, 60, 60));
            g.fillRect(panelX + 35, panelY + 68, 130, 12);
            g.setColor(MP_BLUE);
            g.fillRect(panelX + 35, panelY + 68, (int) (130 * me.mp / (float) me.maxMP), 12);
            g.setColor(Color.WHITE);
            g.drawRect(panelX + 35, panelY + 68, 130, 12);
            g.drawString(me.mp + "/" + me.maxMP, panelX + 80, panelY + 78);

            // Stats
            g.setFont(new Font("Arial", Font.PLAIN, 11));
            g.drawString("ATK: " + me.atk + "  DEF: " + me.def, panelX + 10, panelY + 95);

            // Player list panel
            int listX = W - 170, listY = 60;
            int listH = 30 + players.size() * 25;

            g.setColor(new Color(0, 60, 140, 220));
            g.fillRoundRect(listX, listY, 160, listH, 10, 10);
            g.setColor(UI_BORDER);
            g.drawRoundRect(listX, listY, 160, listH, 10, 10);

            g.setFont(new Font("Arial", Font.BOLD, 14));
            g.setColor(STAR_YELLOW);
            g.drawString("Players Online", listX + 10, listY + 20);

            int py = listY + 40;
            for (PlayerState p : players.values()) {
                g.setColor(p.charClass.color);
                g.fillOval(listX + 10, py - 10, 10, 10);
                g.setColor(Color.WHITE);
                g.setFont(new Font("Arial", Font.PLAIN, 12));
                g.drawString(p.name.substring(0, Math.min(12, p.name.length())), listX + 25, py);
                py += 25;
            }

            // Controls hint
            g.setColor(new Color(0, 0, 0, 150));
            g.fillRoundRect(10, H - 35, 280, 25, 8, 8);
            g.setColor(Color.WHITE);
            g.setFont(new Font("Arial", Font.PLAIN, 12));
            g.drawString("Arrow Keys/WASD: Move | Space/Z: Jump", 20, H - 18);
        }
    }

    // ============================================================
    // CHARACTER SELECT
    // ============================================================
    static class CharacterSelect extends JPanel {
        int selected = 0;
        String playerName = "";
        boolean typingName = true;
        float animTimer = 0;
        JFrame parentFrame;

        CharacterSelect(JFrame parent) {
            this.parentFrame = parent;
            setPreferredSize(new Dimension(W, H));
            setFocusable(true);

            addKeyListener(new KeyAdapter() {
                public void keyPressed(KeyEvent e) {
                    if (typingName) {
                        if (e.getKeyCode() == KeyEvent.VK_ENTER && !playerName.isEmpty()) {
                            typingName = false;
                        } else if (e.getKeyCode() == KeyEvent.VK_BACK_SPACE && !playerName.isEmpty()) {
                            playerName = playerName.substring(0, playerName.length() - 1);
                        } else if (Character.isLetterOrDigit(e.getKeyChar()) && playerName.length() < 12) {
                            playerName += e.getKeyChar();
                        }
                    } else {
                        if (e.getKeyCode() == KeyEvent.VK_LEFT) {
                            selected = (selected - 1 + CharacterClass.values().length) % CharacterClass.values().length;
                        } else if (e.getKeyCode() == KeyEvent.VK_RIGHT) {
                            selected = (selected + 1) % CharacterClass.values().length;
                        } else if (e.getKeyCode() == KeyEvent.VK_ENTER) {
                            startGame();
                        }
                    }
                    repaint();
                }
            });

            Timer timer = new Timer(16, e -> {
                animTimer += 0.1f;
                repaint();
            });
            timer.start();
        }

        void startGame() {
            if (playerName.isEmpty()) {
                playerName = "Player" + (int) (Math.random() * 9999);
            }
            CharacterClass cls = CharacterClass.values()[selected];

            parentFrame.getContentPane().removeAll();
            parentFrame.add(new GamePanel(playerName, cls));
            parentFrame.revalidate();
            parentFrame.repaint();
            parentFrame.getContentPane().getComponent(0).requestFocus();
        }

        protected void paintComponent(Graphics gg) {
            super.paintComponent(gg);
            Graphics2D g = (Graphics2D) gg;
            g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

            // Background gradient
            GradientPaint bg = new GradientPaint(0, 0, new Color(40, 40, 100), 0, H, new Color(80, 60, 140));
            g.setPaint(bg);
            g.fillRect(0, 0, W, H);

            // Stars
            g.setColor(new Color(255, 255, 255, 150));
            Random r = new Random(42);
            for (int i = 0; i < 50; i++) {
                int sx = r.nextInt(W);
                int sy = r.nextInt(H / 2);
                int ss = 1 + r.nextInt(3);
                g.fillOval(sx, sy, ss, ss);
            }

            // Title
            g.setFont(new Font("Arial", Font.BOLD, 48));
            g.setColor(STAR_YELLOW);
            String title = "S!MARIO RPG";
            FontMetrics fm = g.getFontMetrics();
            g.drawString(title, W / 2 - fm.stringWidth(title) / 2, 70);

            g.setFont(new Font("Arial", Font.BOLD, 24));
            g.setColor(Color.WHITE);
            String sub = "Samsoft Edition";
            fm = g.getFontMetrics();
            g.drawString(sub, W / 2 - fm.stringWidth(sub) / 2, 105);

            if (typingName) {
                // Name entry
                g.setFont(new Font("Arial", Font.BOLD, 28));
                g.setColor(Color.WHITE);
                g.drawString("Enter Your Name:", W / 2 - 120, 220);

                // Text box
                g.setColor(new Color(30, 30, 60));
                g.fillRoundRect(W / 2 - 150, 240, 300, 50, 10, 10);
                g.setColor(STAR_YELLOW);
                g.setStroke(new BasicStroke(3));
                g.drawRoundRect(W / 2 - 150, 240, 300, 50, 10, 10);

                String cursor = ((int) (animTimer * 2) % 2 == 0) ? "_" : "";
                g.setFont(new Font("Arial", Font.BOLD, 24));
                g.setColor(Color.WHITE);
                g.drawString(playerName + cursor, W / 2 - 140, 275);

                g.setFont(new Font("Arial", Font.PLAIN, 16));
                g.drawString("Press ENTER to continue", W / 2 - 90, 330);
            } else {
                // Character select
                g.setFont(new Font("Arial", Font.BOLD, 24));
                g.setColor(Color.WHITE);
                g.drawString("Select Your Character:", W / 2 - 110, 160);

                CharacterClass[] classes = CharacterClass.values();
                int cardW = 150, cardH = 280;
                int startX = (W - (classes.length * cardW + (classes.length - 1) * 20)) / 2;

                for (int i = 0; i < classes.length; i++) {
                    CharacterClass c = classes[i];
                    int cx = startX + i * (cardW + 20);
                    int cy = 200;

                    // Card
                    if (i == selected) {
                        g.setColor(STAR_YELLOW);
                        g.setStroke(new BasicStroke(4));
                        g.drawRoundRect(cx - 5, cy - 5, cardW + 10, cardH + 10, 15, 15);
                    }

                    g.setColor(new Color(30, 30, 60, 220));
                    g.fillRoundRect(cx, cy, cardW, cardH, 10, 10);
                    g.setColor(new Color(100, 100, 140));
                    g.setStroke(new BasicStroke(2));
                    g.drawRoundRect(cx, cy, cardW, cardH, 10, 10);

                    // Character sprite
                    int frame = (i == selected) ? (int) animTimer % 4 : 0;
                    float scale = (i == selected) ? 2.5f : 2f;
                    SMRPGSprites.drawCharacter(g, cx + cardW / 2, cy + 100, c, 1, frame, scale);

                    // Name
                    g.setFont(new Font("Arial", Font.BOLD, 16));
                    g.setColor(c.color);
                    fm = g.getFontMetrics();
                    g.drawString(c.name, cx + cardW / 2 - fm.stringWidth(c.name) / 2, cy + 170);

                    // Stats
                    g.setFont(new Font("Arial", Font.PLAIN, 11));
                    g.setColor(Color.WHITE);
                    g.drawString("HP: " + c.baseHP, cx + 10, cy + 195);
                    g.drawString("MP: " + c.baseMP, cx + 80, cy + 195);
                    g.drawString("ATK: " + c.baseATK, cx + 10, cy + 210);
                    g.drawString("DEF: " + c.baseDEF, cx + 80, cy + 210);

                    // Description
                    g.setFont(new Font("Arial", Font.ITALIC, 10));
                    g.setColor(new Color(200, 200, 200));
                    // Word wrap description
                    String[] words = c.description.split(" ");
                    StringBuilder line = new StringBuilder();
                    int ly = cy + 235;
                    for (String word : words) {
                        if (g.getFontMetrics().stringWidth(line + word) > cardW - 20) {
                            g.drawString(line.toString(), cx + 10, ly);
                            line = new StringBuilder();
                            ly += 12;
                        }
                        line.append(word).append(" ");
                    }
                    if (!line.isEmpty()) {
                        g.drawString(line.toString(), cx + 10, ly);
                    }
                }

                // Controls
                g.setFont(new Font("Arial", Font.PLAIN, 14));
                g.setColor(Color.WHITE);
                g.drawString("← → to select | ENTER to confirm", W / 2 - 120, H - 60);
            }

            // Auto-online badge
            g.setColor(new Color(100, 200, 255));
            g.setFont(new Font("Arial", Font.PLAIN, 12));
            g.drawString("★ Auto Online — DS Download Play Style ★", W / 2 - 130, H - 30);
        }
    }

    // ============================================================
    // MAIN
    // ============================================================
    public static void main(String[] args) {
        System.out.println("═".repeat(60));
        System.out.println("  S!MARIO RPG — Samsoft Edition");
        System.out.println("  Super Mario RPG Style Engine");
        System.out.println("═".repeat(60));
        System.out.println("\n  ★ Auto Join or Auto Host (no manual server needed)");
        System.out.println("  ★ DS Download Play style discovery");
        System.out.println("  ★ Super Mario RPG (SNES) graphics");
        System.out.println("  ★ Classes: Human, Koopa, Toad, Goomba, Yoshi");
        System.out.println("═".repeat(60));

        SwingUtilities.invokeLater(() -> {
            JFrame f = new JFrame(TITLE);
            f.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            f.setResizable(false);
            f.add(new CharacterSelect(f));
            f.pack();
            f.setLocationRelativeTo(null);
            f.setVisible(true);
        });
    }
}
