Develop a Python-based ETL pipeline that ingests log files, parses relevant information, and stores it in a SQL database. The pipeline will utilize FFmpeg to process media files as part of the data transformation step. Each milestone incrementally verifies the database connection, log parsing functionality, and the overall ETL process to ensure the full pipeline works seamlessly.

## Milestone 1: Set up Database Connection

### Objective
Establish a SQLite database connection and create the necessary tables for storing log entries and media metadata. Additionally, create a marker file to indicate successful completion.

### Required Artifacts
1. **hello.txt** - A marker file in `/app` containing the text "Hello, world!"
2. **etl_pipeline.db** - A SQLite database created at `/app/etl_pipeline.db`
3. **log_entries table** - Created with the following schema:

| Column Name  | Type      | Constraints |
| ------------ | --------- | ----------- |
| id           | INTEGER   | PRIMARY KEY |
| timestamp    | TEXT      | NOT NULL    |
| level        | TEXT      | NOT NULL    |
| message      | TEXT      | NOT NULL    |
| source_file  | TEXT      |             |
| processed_at | TIMESTAMP | NOT NULL    |

4. **media_metadata table** - Created with the following schema:

| Column Name  | Type      | Constraints |
| ------------ | --------- | ----------- |
| id           | INTEGER   | PRIMARY KEY |
| log_entry_id | INTEGER   | NOT NULL, FOREIGN KEY REFERENCES log_entries(id) |
| media_file   | TEXT      | NOT NULL    |
| duration     | REAL      |             |
| format       | TEXT      |             |
| bitrate      | INTEGER   |             |
| processed_at | TIMESTAMP | NOT NULL    |

### Implementation Details
Create a `DatabaseConnection` class that:
- Establishes a connection to SQLite database (`etl_pipeline.db`)
- Creates the two tables with proper schema and foreign key relationships
- Handles errors gracefully with try-catch blocks

### Validation
The tests will verify:
- `/app/hello.txt` exists and contains "Hello, world!"
- `/app/etl_pipeline.db` exists
- Both `log_entries` and `media_metadata` tables exist
- Both tables have all required columns
- Foreign key relationship is established between the tables
