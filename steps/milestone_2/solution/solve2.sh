#!/bin/bash
set -euo pipefail

APP_DIR="${APP_DIR:-/app}"
mkdir -p "$APP_DIR/logs"

# Milestone 2: Implement Log Parsing Script

# Create the log parser script in the application directory
cat > "$APP_DIR/log_parser.py" << 'EOF'
import sqlite3
import re
import os
from pathlib import Path
from datetime import datetime

class LogParser:
    """Parse log files and insert data into the database."""
    
    LOG_PATTERN = r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\s+\[(\w+)\]\s+(.+?)\s+-\s+Source:\s+(.+)$'
    
    def __init__(self, db_path=None):
        self.db_path = db_path or os.path.join(os.environ.get("APP_DIR", "/app"), "etl_pipeline.db")
        self.conn = None
        
    def connect(self):
        """Connect to the database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            print(f"Connected to database: {self.db_path}")
            return True
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def parse_log_file(self, log_file):
        """Parse a single log file and insert entries into the database."""
        if not self.conn:
            print("No database connection.")
            return False
        
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            cursor = self.conn.cursor()
            inserted = 0
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                match = re.match(self.LOG_PATTERN, line)
                if match:
                    timestamp, level, message, source_file = match.groups()
                    
                    cursor.execute(
                        """
                        INSERT INTO log_entries (timestamp, level, message, source_file)
                        VALUES (?, ?, ?, ?)
                        """,
                        (timestamp, level.upper(), message.strip(), source_file.strip())
                    )
                    inserted += 1
            
            self.conn.commit()
            print(f"Inserted {inserted} log entries from {log_file}")
            return True
            
        except Exception as e:
            print(f"Error parsing log file {log_file}: {e}")
            return False
    
    def parse_logs_from_directory(self, log_dir):
        """Parse all log files in a directory."""
        log_path = Path(log_dir)
        if not log_path.exists():
            print(f"Log directory does not exist: {log_dir}")
            return False
        
        log_files = list(log_path.glob("*.log"))
        print(f"Found {len(log_files)} log files")
        
        for log_file in log_files:
            self.parse_log_file(str(log_file))
        
        return True
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

def main():
    """Main function to parse logs."""
    parser = LogParser()
    if parser.connect():
        parser.parse_logs_from_directory(os.path.join(os.environ.get("APP_DIR", "/app"), "logs"))
        parser.close()
        print("Log parsing complete.")
    else:
        print("Failed to connect to database.")

if __name__ == "__main__":
    main()
EOF

# Create the logs directory if it doesn't exist
mkdir -p "$APP_DIR/logs"

# Create sample log files for testing
cat > "$APP_DIR/logs/application.log" << 'EOF'
2024-05-07 10:15:23 [INFO] Application started - Source: app.py
2024-05-07 10:15:24 [DEBUG] Loading configuration file - Source: config.py
2024-05-07 10:15:25 [INFO] Database connection established - Source: db.py
2024-05-07 10:15:26 [WARNING] Cache miss on user lookup - Source: cache.py
2024-05-07 10:15:27 [ERROR] Failed to process user request - Source: handler.py
EOF

cat > "$APP_DIR/logs/system.log" << 'EOF'
2024-05-07 10:20:01 [INFO] System health check started - Source: health.py
2024-05-07 10:20:02 [DEBUG] CPU usage at 45% - Source: metrics.py
2024-05-07 10:20:03 [INFO] Memory usage at 2.5GB - Source: metrics.py
2024-05-07 10:20:04 [WARNING] Disk space running low - Source: storage.py
2024-05-07 10:20:05 [CRITICAL] Service unavailable - Source: service.py
EOF

# Run the log parser
python3 "$APP_DIR/log_parser.py"

# Create the milestone 2 done marker
touch "$APP_DIR/milestone2_done.txt"

echo "Milestone 2 complete: Log parsing script implemented and executed."

