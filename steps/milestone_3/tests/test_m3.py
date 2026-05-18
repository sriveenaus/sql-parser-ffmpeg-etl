"""Tests for milestone 3. Run alone with: pytest tests/test_m3.py"""

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


class TestMilestone3:
    """Tests for milestone 3: ETL Pipeline with FFmpeg."""

    def test_milestone_1_artifact_persists(self) -> None:
        """The /app/hello.txt file from milestone 1 must still exist."""
        hello_path = APP_DIR / "hello.txt"
        assert hello_path.exists(), (
            f"File {hello_path} does not exist — was milestone 1 completed?"
        )

    def test_milestone_2_artifact_persists(self) -> None:
        """The /app/milestone2_done.txt file from milestone 2 must still exist."""
        done_path = APP_DIR / "milestone2_done.txt"
        assert done_path.exists(), f"File {done_path} does not exist — was milestone 2 completed?"

    def test_milestone_3_done_file_exists(self) -> None:
        """The /app/milestone3_done.txt file must exist."""
        done_path = APP_DIR / "milestone3_done.txt"
        assert done_path.exists(), f"File {done_path} does not exist"

    def test_media_processor_script_exists(self) -> None:
        """The media processor script must exist in /app."""
        processor_path = APP_DIR / "media_processor.py"
        assert processor_path.exists(), f"Media processor script {processor_path} does not exist"

    def test_sample_media_files_created(self) -> None:
        """Sample media files must be created in /app/media."""
        media_dir = APP_DIR / "media"
        assert media_dir.exists(), f"Media directory {media_dir} does not exist"
        media_files = list(media_dir.glob("*"))
        assert len(media_files) > 0, "No media files found in /app/media"

    def test_media_metadata_stored_in_database(self) -> None:
        """Media metadata must be processed and stored in the media_metadata table."""
        db_path = APP_DIR / "etl_pipeline.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM media_metadata")
        count = cursor.fetchone()[0]
        conn.close()
        assert count > 0, "No media metadata found in the database"

    def test_media_metadata_has_correct_data(self) -> None:
        """Media metadata entries must have all required fields populated."""
        db_path = APP_DIR / "etl_pipeline.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, log_entry_id, media_file, duration, format, bitrate 
            FROM media_metadata 
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None, "No media metadata found in database"
        id_val, log_entry_id, media_file, duration, format_val, bitrate = row
        
        assert id_val is not None and id_val > 0, "ID should be a positive integer"
        assert media_file is not None and len(media_file) > 0, "Media file should not be empty"
        # Duration, format, and bitrate may be None for test files, but media_file should exist

    def test_log_entries_persist(self) -> None:
        """Log entries from milestone 2 must still be in the database."""
        db_path = APP_DIR / "etl_pipeline.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM log_entries")
        count = cursor.fetchone()[0]
        conn.close()
        assert count > 0, "Log entries from milestone 2 have been deleted"

    def test_foreign_key_relationships_maintained(self) -> None:
        """Foreign key relationships between tables must be maintained."""
        db_path = APP_DIR / "etl_pipeline.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check foreign key constraint exists
        cursor.execute("PRAGMA foreign_key_list(media_metadata)")
        foreign_keys = cursor.fetchall()
        conn.close()
        
        assert len(foreign_keys) > 0, "Foreign key relationship not found"

    def test_media_metadata_links_to_existing_log_entries(self) -> None:
        """Media rows must contain populated foreign keys to real log entries."""
        db_path = APP_DIR / "etl_pipeline.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM media_metadata AS media
            LEFT JOIN log_entries AS logs ON media.log_entry_id = logs.id
            WHERE media.log_entry_id IS NULL OR logs.id IS NULL
            """
        )
        unlinked_count = cursor.fetchone()[0]
        conn.close()

        assert unlinked_count == 0, (
            "Every media_metadata row must reference an existing log_entries row"
        )

    def test_unsupported_media_files_are_skipped_without_crashing(self, tmp_path: Path) -> None:
        """Unsupported media files should not crash processing or create rows."""
        processor_path = APP_DIR / "media_processor.py"
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
        cursor.execute(
            """
            CREATE TABLE media_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_entry_id INTEGER NOT NULL,
                media_file TEXT NOT NULL,
                duration REAL,
                format TEXT,
                bitrate INTEGER,
                processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (log_entry_id) REFERENCES log_entries (id)
            )
            """
        )
        conn.commit()
        conn.close()

        media_dir = tmp_path / "media"
        media_dir.mkdir()
        (media_dir / "unsupported.xyz").write_text("unsupported media content")

        module = load_module(processor_path, "milestone3_media_processor_under_test")
        processor = module.MediaProcessor(db_path=str(db_path))

        assert processor.connect(), "MediaProcessor could not connect to test database"
        try:
            processor.process_media_directory(str(media_dir))
        finally:
            processor.close()

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM media_metadata")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 0, "Unsupported media files should be skipped, not inserted"

    def test_etl_pipeline_complete(self) -> None:
        """The complete ETL pipeline should have data in all tables."""
        db_path = APP_DIR / "etl_pipeline.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check log_entries table
        cursor.execute("SELECT COUNT(*) FROM log_entries")
        log_count = cursor.fetchone()[0]
        
        # Check media_metadata table
        cursor.execute("SELECT COUNT(*) FROM media_metadata")
        media_count = cursor.fetchone()[0]
        
        conn.close()
        
        assert log_count > 0, "No log entries found (Milestone 2 data missing)"
        assert media_count > 0, "No media metadata found (Milestone 3 processing failed)"
