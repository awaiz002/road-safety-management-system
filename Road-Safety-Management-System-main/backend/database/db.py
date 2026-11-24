import sqlite3
import os
import hashlib

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "road_safety.db")
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")
SEED_PATH = os.path.join(DB_DIR, "seed.sql")

def get_db_connection():
    """Establish and return an SQLite database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password: str) -> str:
    """Return SHA-256 hash of password for security."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db(force: bool = False):
    """
    Initialize database schema, seed base rules/users, and automatically
    fetch & populate Vijay Nagar Square previous accident records from OpenStreetMap & Weather Open APIs.
    """
    db_exists = os.path.exists(DB_PATH)
    if not db_exists or force:
        print(f"[*] Initializing database at {DB_PATH}...")
        conn = get_db_connection()
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        
        # Check if already seeded base users and rules
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            print("[*] Seeding database with users, traffic rules & emergency contacts...")
            with open(SEED_PATH, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
                
        # Automatically generate and populate Vijay Nagar Square accident data via Open API
        cursor.execute("SELECT COUNT(*) FROM accidents")
        accidents_count = cursor.fetchone()[0]
        conn.commit()
        conn.close()

        if accidents_count == 0:
            print("[*] Automatically fetching & populating previous accident data via OpenStreetMap & Open-Meteo APIs...")
            try:
                from utils.open_api_generator import generate_accidents_from_open_api
            except ModuleNotFoundError:
                from backend.utils.open_api_generator import generate_accidents_from_open_api
            generate_accidents_from_open_api(count=20, clear_existing=False)
            print("[+] Previous accident data automatically generated & loaded into SQLite via Open API.")

        print("[+] Database initialized successfully.")
    else:
        # Ensure schema tables exist even if file exists
        conn = get_db_connection()
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM accidents")
        accidents_count = cursor.fetchone()[0]
        conn.commit()
        conn.close()

        if accidents_count == 0:
            print("[*] Automatically populating empty accidents table via Open API pipeline...")
            try:
                from utils.open_api_generator import generate_accidents_from_open_api
            except ModuleNotFoundError:
                from backend.utils.open_api_generator import generate_accidents_from_open_api
            generate_accidents_from_open_api(count=20, clear_existing=False)
            print("[+] Previous accident data automatically loaded into SQLite via Open API.")

if __name__ == "__main__":
    init_db(force=True)
