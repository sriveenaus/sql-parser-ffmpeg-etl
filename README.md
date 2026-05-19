# SQLite + FFmpeg ETL Pipeline
Develop a Python-based ETL pipeline that ingests log files, parses relevant information, and stores it in a SQL database. The pipeline will utilize FFmpeg to process media files as part of the data transformation step.

## Project Overview

This project consists of 3 milestones:
1. **Milestone 1**: Set up database connection and create tables
2. **Milestone 2**: Implement log parsing script
3. **Milestone 3**: Complete ETL pipeline with FFmpeg media processing

## Database Schema

### log_entries Table

| Column Name  | Type      | Constraints                                               |
| ------------ | --------- | --------------------------------------------------------- |
| id           | INTEGER   | PRIMARY KEY AUTOINCREMENT                                 |
| timestamp    | TEXT      | NOT NULL                                                  |
| level        | TEXT      | NOT NULL, CHECK constraint: `level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')` |
| message      | TEXT      | NOT NULL                                                  |
| source_file  | TEXT      |                                                           |
| processed_at | TIMESTAMP | NOT NULL DEFAULT CURRENT_TIMESTAMP                         |

Valid log levels are: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

### media_metadata Table

| Column Name  | Type      | Constraints                                    |
| ------------ | --------- | ---------------------------------------------- |
| id           | INTEGER   | PRIMARY KEY AUTOINCREMENT                      |
| log_entry_id | INTEGER   | NOT NULL, FOREIGN KEY REFERENCES log_entries(id)|
| media_file   | TEXT      | NOT NULL                                       |
| duration     | REAL      |                                                |
| format       | TEXT      |                                                |
| bitrate      | INTEGER   |                                                |
| processed_at | TIMESTAMP | NOT NULL DEFAULT CURRENT_TIMESTAMP              |

## Required Files

- `/app/hello.txt` - Contains "Hello, world!"
- `/app/etl_pipeline.db` - SQLite database
- `/app/log_parser.py` - Log parsing module
- `/app/media_processor.py` - Media processing module
- `/app/milestone2_done.txt` - Milestone 2 completion marker
- `/app/milestone3_done.txt` - Milestone 3 completion marker

<img width="1713" height="989" alt="Screenshot from 2026-05-18 22-46-45" src="https://github.com/user-attachments/assets/e84987ce-74ff-4140-afef-c0d8a658628f" />


