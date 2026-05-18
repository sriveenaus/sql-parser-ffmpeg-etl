"""Tests for milestone 2. Run alone with: pytest tests/test_m2.py"""

import importlib.util
import os
from pathlib import Path
import sqlite3


APP_DIR = Path(os.environ.get("APP_DIR", "/app"))


def load_module(module_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None and spec.loader is not None, (
        f"Could not load module from {module_path}"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestMilestone2:
    """Tests for milestone 2: Log Parsing Script."""

    def test_milestone_1_artifact_persists(self) -> None:
        """The /app/hello.txt file from milestone 1 must still exist (files persist across milestones)."""
        hello_path = APP_DIR / "hello.txt"
        assert hello_path.exists(), (
            f"File {hello_path} does not exist — was milestone 1 completed?"
        )

    def test_milestone_2_done_file_exists(self) -> None:
        """The /app/milestone2_done.txt file must exist."""
        done_path = APP_DIR / "milestone2_done.txt"
        assert done_path.exists(), f"File {done_path} does not exist"

    def test_log_parser_script_exists(self) -> None:
        """The log parser script must exist in /app."""
        parser_path = APP_DIR / "log_parser.py"
        assert parser_path.exists(), f"Log parser script {parser_path} does not exist"

    def test_sample_logs_created(self) -> None:
        """Sample log files must be created for testing."""
        logs_dir = APP_DIR / "logs"
        assert logs_dir.exists(), f"Logs directory {logs_dir} does not exist"
        log_files = list(logs_dir.glob("*.log"))
        assert len(log_files) > 0, "No log files found in /app/logs"

    def test_logs_parsed_into_database(self) -> None:
        """Log entries must be parsed and inserted into the log_entries table."""
        db_path = APP_DIR / "etl_pipeline.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM log_entries")
        count = cursor.fetchone()[0]
        conn.close()
        assert count > 0, "No logs were parsed into the database"

    def test_log_entries_have_correct_data(self) -> None:
        """Log entries must have all required fields populated."""
        db_path = APP_DIR / "etl_pipeline.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, timestamp, level, message, source_file 
            FROM log_entries 
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None, "No log entries found in database"
        id_val, timestamp, level, message, source_file = row
        
        assert id_val is not None and id_val > 0, "ID should be a positive integer"
        assert timestamp is not None and len(timestamp) > 0, "Timestamp should not be empty"
        assert level is not None and level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], (
            f"Level should be valid, got: {level}"
        )
        assert message is not None and len(message) > 0, "Message should not be empty"
        assert source_file is not None and len(source_file) > 0, "Source file should not be empty"

    def test_database_connection_persists(self) -> None:
        """The database from milestone 1 must still be accessible."""
        db_path = APP_DIR / "etl_pipeline.db"
        assert db_path.exists(), "Database file does not exist"
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert "log_entries" in tables, "log_entries table not found"
        assert "media_metadata" in tables, "media_metadata table not found"

    def test_malformed_log_lines_are_skipped_without_crashing(self, tmp_path: Path) -> None:
        """Malformed log lines should not crash the parser or create bad rows."""
        parser_path = APP_DIR / "log_parser.py"
        db_path = tmp_path / "etl_pipeline.db"

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE log_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                source_file TEXT,
                processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        conn.close()

        malformed_log = tmp_path / "malformed.log"
        malformed_log.write_text(
            "not a valid log entry\n"
            "2024-05-07 10:15:23 [BOGUS] message without source\n"
        )

        module = load_module(parser_path, "milestone2_log_parser_under_test")
        parser = module.LogParser(db_path=str(db_path))

        assert parser.connect(), "LogParser could not connect to test database"
        try:
            parser.parse_log_file(str(malformed_log))
        finally:
            parser.close()

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM log_entries")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 0, "Malformed log lines should be skipped, not inserted"
