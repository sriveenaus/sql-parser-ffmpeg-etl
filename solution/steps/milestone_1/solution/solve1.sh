#!/bin/bash
set -euo pipefail

APP_DIR="${APP_DIR:-/app}"
mkdir -p "$APP_DIR"

cat > "$APP_DIR/database.py" << 'EOF'
import sqlite3
import os
from datetime import datetime

APP_DIR = os.environ.get("APP_DIR", "/app")
DB_PATH = os.path.join(APP_DIR, "etl_pipeline.db")

class DatabaseConnection:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Establish connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            print(f"Successfully connected to database: {self.db_path}")
            return True
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            return False

    def create_tables(self):
        """Create necessary tables for the ETL pipeline."""
        if not self.conn:
            print("No database connection available.")
            return False

        try:
            cursor = self.conn.cursor()

            # Table for parsed log entries
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS log_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
                    message TEXT NOT NULL,
                    source_file TEXT,
                    processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Table for media processing results (linked to log entries)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS media_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    log_entry_id INTEGER NOT NULL,
                    media_file TEXT NOT NULL,
                    duration REAL,
                    format TEXT,
                    bitrate INTEGER,
                    processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (log_entry_id) REFERENCES log_entries (id)
                )
            ''')

            self.conn.commit()
            print("Database tables created successfully.")
            return True
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
            return False

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")


def setup_database():
    """Main function to set up the database for Milestone 1."""
    db = DatabaseConnection()
    if db.connect():
        if db.create_tables():
            print("Database setup complete for ETL pipeline.")
            return True
        else:
            print("Failed to create tables.")
            return False
    else:
        print("Failed to connect to database.")
        return False
    db.close()


if __name__ == "__main__":
    setup_database()
EOF

python3 "$APP_DIR/database.py"

echo "Hello, world!" > "$APP_DIR/hello.txt"

test -f "$APP_DIR/etl_pipeline.db" && echo "Database setup complete: $APP_DIR/etl_pipeline.db"
