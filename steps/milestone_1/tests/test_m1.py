"""Tests for milestone 1. Run alone with: pytest tests/test_m1.py"""

from pathlib import Path
import os
import sqlite3


APP_DIR = Path(os.environ.get("APP_DIR", "/app"))


class TestMilestone1:
    """Tests for milestone 1: Database Connection Setup."""

    def test_milestone_1_file_exists(self) -> None:
        """The /app/hello.txt file must exist."""
        hello_path = APP_DIR / "hello.txt"
        assert hello_path.exists(), f"File {hello_path} does not exist"

    def test_milestone_1_file_contents(self) -> None:
        """The /app/hello.txt file must contain 'Hello, world!'."""
        hello_path = APP_DIR / "hello.txt"
        assert hello_path.read_text().strip() == "Hello, world!", (
            f"Expected 'Hello, world!' but got '{hello_path.read_text().strip()}'"
        )

    def test_database_file_exists(self) -> None:
        """The /app/etl_pipeline.db file must exist."""
        db_path = APP_DIR / "etl_pipeline.db"
        assert db_path.exists(), f"Database file {db_path} does not exist"

    def test_log_entries_table_exists(self) -> None:
        """The log_entries table must exist in the database."""
        db_path = APP_DIR / "etl_pipeline.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='log_entries'")
        result = cursor.fetchone()
        conn.close()
        assert result is not None, "log_entries table does not exist"

    def test_media_metadata_table_exists(self) -> None:
        """The media_metadata table must exist in the database."""
        db_path = APP_DIR / "etl_pipeline.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='media_metadata'")
        result = cursor.fetchone()
        conn.close()
        assert result is not None, "media_metadata table does not exist"

    def test_log_entries_schema(self) -> None:
        """The log_entries table must have the correct columns."""
        db_path = APP_DIR / "etl_pipeline.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(log_entries)")
        column_info = {row[1]: row for row in cursor.fetchall()}
        conn.close()
        required_columns = {'id', 'timestamp', 'level', 'message', 'source_file', 'processed_at'}
        columns = set(column_info)
        assert required_columns.issubset(columns), (
            f"log_entries table missing columns. Expected {required_columns}, got {columns}"
        )
        for column in ("timestamp", "level", "message"):
            assert column_info[column][3] == 1, (
                f"log_entries.{column} must be declared NOT NULL"
            )
        assert column_info["processed_at"][2].upper() == "TIMESTAMP", (
            "log_entries.processed_at must be declared as TIMESTAMP"
        )
        assert column_info["processed_at"][3] == 1, (
            "log_entries.processed_at must be declared NOT NULL"
        )

    def test_media_metadata_schema(self) -> None:
        """The media_metadata table must have the correct columns."""
        db_path = APP_DIR / "etl_pipeline.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(media_metadata)")
        column_info = {row[1]: row for row in cursor.fetchall()}
        conn.close()
        columns = set(column_info)
        required_columns = {'id', 'log_entry_id', 'media_file', 'duration', 'format', 'bitrate', 'processed_at'}
        assert required_columns.issubset(columns), (
            f"media_metadata table missing columns. Expected {required_columns}, got {columns}"
        )
        assert column_info["log_entry_id"][3] == 1, (
            "media_metadata.log_entry_id must be declared NOT NULL"
        )
        assert column_info["processed_at"][2].upper() == "TIMESTAMP", (
            "media_metadata.processed_at must be declared as TIMESTAMP"
        )
        assert column_info["processed_at"][3] == 1, (
            "media_metadata.processed_at must be declared NOT NULL"
        )

    def test_foreign_key_relationship(self) -> None:
        """The media_metadata table must have a foreign key to log_entries."""
        db_path = APP_DIR / "etl_pipeline.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_key_list(media_metadata)")
        foreign_keys = cursor.fetchall()
        conn.close()
        assert len(foreign_keys) > 0, "No foreign key relationship found between media_metadata and log_entries"
