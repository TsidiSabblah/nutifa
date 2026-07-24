import sqlite3
import os

# Use a writable directory on Render
if os.environ.get('RENDER'):
    DB_PATH = '/tmp/hajilala.db'
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "hajilala.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            email         TEXT UNIQUE NOT NULL,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role          TEXT DEFAULT 'fan',
            full_name     TEXT,
            avatar        TEXT,
            country       TEXT DEFAULT 'Ghana',
            phone         TEXT,
            bio           TEXT,
            is_active     INTEGER DEFAULT 1,
            created_at    TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Artist profiles table
    c.execute("""
        CREATE TABLE IF NOT EXISTS artist_profiles (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER UNIQUE NOT NULL REFERENCES users(id),
            stage_name      TEXT NOT NULL,
            genre           TEXT,
            country         TEXT,
            cover_image     TEXT,
            social_links    TEXT,
            payout_method   TEXT,
            payout_details  TEXT,
            total_earnings  REAL DEFAULT 0.0,
            is_verified     INTEGER DEFAULT 0,
            created_at      TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Albums table
    c.execute("""
        CREATE TABLE IF NOT EXISTS albums (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id    INTEGER NOT NULL REFERENCES artist_profiles(id),
            title        TEXT NOT NULL,
            cover_image  TEXT,
            description  TEXT,
            price        REAL DEFAULT 0.0,
            currency     TEXT DEFAULT 'GHS',
            is_published INTEGER DEFAULT 0,
            created_at   TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tracks table with new copyright columns
    c.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id     INTEGER NOT NULL REFERENCES artist_profiles(id),
            album_id      INTEGER REFERENCES albums(id),
            title         TEXT NOT NULL,
            file_path     TEXT NOT NULL,
            preview_path  TEXT,
            cover_image   TEXT,
            duration      INTEGER,
            track_type    TEXT DEFAULT 'song',
            price         REAL DEFAULT 0.0,
            currency      TEXT DEFAULT 'GHS',
            plays         INTEGER DEFAULT 0,
            downloads     INTEGER DEFAULT 0,
            is_published  INTEGER DEFAULT 0,
            created_at    TEXT DEFAULT CURRENT_TIMESTAMP,
            copyright_certified_at TEXT DEFAULT NULL,
            copyright_certified_ip TEXT DEFAULT NULL
        )
    """)

    # Music videos table
    c.execute("""
        CREATE TABLE IF NOT EXISTS music_videos (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id    INTEGER NOT NULL REFERENCES artist_profiles(id),
            track_id     INTEGER REFERENCES tracks(id),
            title        TEXT NOT NULL,
            video_path   TEXT,
            youtube_url  TEXT,
            thumbnail    TEXT,
            price        REAL DEFAULT 0.0,
            currency     TEXT DEFAULT 'GHS',
            views        INTEGER DEFAULT 0,
            is_published INTEGER DEFAULT 0,
            created_at   TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Merchandise table
    c.execute("""
        CREATE TABLE IF NOT EXISTS merchandise (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id    INTEGER NOT NULL REFERENCES artist_profiles(id),
            name         TEXT NOT NULL,
            description  TEXT,
            image        TEXT,
            price        REAL NOT NULL,
            currency     TEXT DEFAULT 'GHS',
            sizes        TEXT,
            stock        INTEGER DEFAULT 0,
            is_published INTEGER DEFAULT 0,
            created_at   TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Orders table
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            buyer_id        INTEGER REFERENCES users(id),
            buyer_email     TEXT NOT NULL,
            item_type       TEXT NOT NULL,
            item_id         INTEGER NOT NULL,
            artist_id       INTEGER NOT NULL REFERENCES artist_profiles(id),
            amount          REAL NOT NULL,
            currency        TEXT DEFAULT 'GHS',
            platform_cut    REAL NOT NULL,
            artist_earnings REAL NOT NULL,
            payment_method  TEXT,
            payment_ref     TEXT,
            status          TEXT DEFAULT 'pending',
            download_token  TEXT,
            created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
            paid_at         TEXT
        )
    """)

    # Payouts table
    c.execute("""
        CREATE TABLE IF NOT EXISTS payouts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id  INTEGER NOT NULL REFERENCES artist_profiles(id),
            amount     REAL NOT NULL,
            currency   TEXT DEFAULT 'GHS',
            method     TEXT,
            reference  TEXT,
            status     TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            sent_at    TEXT,
            payout_details TEXT
        )
    """)

    # Settings table
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # Add missing columns to existing tracks table if they don't exist
    try:
        c.execute("ALTER TABLE tracks ADD COLUMN copyright_certified_at TEXT DEFAULT NULL")
        print("Added copyright_certified_at column")
    except sqlite3.OperationalError:
        print("copyright_certified_at column already exists")
    
    try:
        c.execute("ALTER TABLE tracks ADD COLUMN copyright_certified_ip TEXT DEFAULT NULL")
        print("Added copyright_certified_ip column")
    except sqlite3.OperationalError:
        print("copyright_certified_ip column already exists")
    
    try:
        c.execute("ALTER TABLE payouts ADD COLUMN payout_details TEXT DEFAULT NULL")
        print("Added payout_details column")
    except sqlite3.OperationalError:
        print("payout_details column already exists")

    # Default settings
    defaults = {
        "platform_name":      "Hajilala",
        "platform_cut_pct":   "15",
        "currency_default":   "GHS",
        "paystack_enabled":   "1",
        "flutterwave_enabled":"1",
        "stripe_enabled":     "1",
        "maintenance_mode":   "0",
    }
    for k, v in defaults.items():
        c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

    conn.commit()
    conn.close()
    print("Database ready at:", DB_PATH)

def seed_admin(email, username, password):
    from werkzeug.security import generate_password_hash
    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO users (email, username, password_hash, role, full_name)
            VALUES (?, ?, ?, 'admin', 'Hajilala Admin')
        """, (email, username, generate_password_hash(password)))
        conn.commit()
        print(f"Admin created: {email}")
    except sqlite3.IntegrityError:
        print("Admin already exists.")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    seed_admin("admin@hajilala.music", "admin", "changeme123")
    print("Hajilala database ready!")