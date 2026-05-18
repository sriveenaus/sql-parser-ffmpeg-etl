import importlib.util
import os
import sqlite3
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def app_dir() -> Path:
    return Path(os.environ.get("APP_DIR", "/app"))


def load_module(module_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None and spec.loader is not None, (
        f"Could not load module from {module_path}"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_solution_and_create_database(app_dir: Path) -> None:
    db_path = app_dir / "etl_pipeline.db"
    hello_path = app_dir / "hello.txt"

    assert db_path.exists(), "Database file was not created"
    assert hello_path.exists(), "hello.txt was not created"

    content = hello_path.read_text().strip()
    assert content == "Hello, world!", (
        "hello.txt must contain exactly 'Hello, world!'"
    )


def test_log_entries_table_exists(app_dir: Path) -> None:
    conn = sqlite3.connect(app_dir / "etl_pipeline.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name='log_entries'"
    )

    assert cursor.fetchone() is not None, (
        "log_entries table does not exist"
    )

    conn.close()


def test_media_metadata_table_exists(app_dir: Path) -> None:
    conn = sqlite3.connect(app_dir / "etl_pipeline.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name='media_metadata'"
    )

    assert cursor.fetchone() is not None, (
        "media_metadata table does not exist"
    )

    conn.close()


def test_log_entries_have_rows(app_dir: Path) -> None:
    conn = sqlite3.connect(app_dir / "etl_pipeline.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM log_entries")
    count = cursor.fetchone()[0]

    conn.close()

    assert count >= 1, (
        "No rows were inserted into log_entries"
    )


def test_media_metadata_have_rows(app_dir: Path) -> None:
    conn = sqlite3.connect(app_dir / "etl_pipeline.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM media_metadata")
    count = cursor.fetchone()[0]

    conn.close()

    assert count >= 1, (
        "No rows were inserted into media_metadata"
    )


def test_log_entries_not_null_constraints(app_dir: Path) -> None:
    conn = sqlite3.connect(app_dir / "etl_pipeline.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(log_entries)")
    columns = {row[1]: row for row in cursor.fetchall()}

    conn.close()

    for column in ("timestamp", "level", "message"):
        assert columns[column][3] == 1, (
            f"log_entries.{column} must be declared NOT NULL"
        )
    assert columns["processed_at"][2].upper() == "TIMESTAMP", (
        "log_entries.processed_at must be declared as TIMESTAMP"
    )
    assert columns["processed_at"][3] == 1, (
        "log_entries.processed_at must be declared NOT NULL"
    )


def test_media_metadata_link_schema(app_dir: Path) -> None:
    conn = sqlite3.connect(app_dir / "etl_pipeline.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(media_metadata)")
    columns = {row[1]: row for row in cursor.fetchall()}

    cursor.execute("PRAGMA foreign_key_list(media_metadata)")
    foreign_keys = cursor.fetchall()

    conn.close()

    assert columns["log_entry_id"][3] == 1, (
        "media_metadata.log_entry_id must be declared NOT NULL"
    )
    assert columns["processed_at"][2].upper() == "TIMESTAMP", (
        "media_metadata.processed_at must be declared as TIMESTAMP"
    )
    assert columns["processed_at"][3] == 1, (
        "media_metadata.processed_at must be declared NOT NULL"
    )
    assert any(
        fk[2] == "log_entries" and fk[3] == "log_entry_id" and fk[4] == "id"
        for fk in foreign_keys
    ), "media_metadata.log_entry_id must reference log_entries.id"


def test_malformed_log_lines_do_not_crash_or_insert(
    app_dir: Path, tmp_path: Path
) -> None:
    parser_path = app_dir / "log_parser.py"
    assert parser_path.exists(), "log_parser.py must exist to parse logs"

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

    malformed_log = tmp_path / "malformed.log"
    malformed_log.write_text(
        "not a valid log line\n"
        "2024-05-07 10:15:23 [NOPE] missing expected source suffix\n"
    )

    module = load_module(parser_path, "log_parser_under_test")
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


def test_unsupported_media_files_do_not_crash_or_insert(
    app_dir: Path, tmp_path: Path
) -> None:
    processor_path = app_dir / "media_processor.py"
    assert processor_path.exists(), "media_processor.py must exist"

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

    module = load_module(processor_path, "media_processor_under_test")
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


def test_media_metadata_links_to_existing_log_entries(app_dir: Path) -> None:
    conn = sqlite3.connect(app_dir / "etl_pipeline.db")
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
