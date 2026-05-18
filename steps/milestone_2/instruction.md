## Milestone 2: Implement Log Parsing Script

### Objective
Create a log parsing script that:
1. Reads log entries from log files
2. Parses the log data (timestamp, level, message, source file)
3. Inserts parsed data into the `log_entries` table in the database
4. Creates a marker file to indicate successful completion

### Required Artifacts
1. **log_parser.py** - A Python module in `/app` that implements log parsing functionality
2. **milestone2_done.txt** - A marker file in `/app` created after milestone 2 completes
3. **Sample log files** - Create test log files to parse and load into the database

### log_parser.py Implementation
The module must:
- Have a function or class that reads log files
- Parse log entries extracting: timestamp, level, message, source_file
- Normalize or validate each parsed log level so it is one of:
  `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`
- Insert parsed entries into the `log_entries` table using the database connection from Milestone 1
- Handle errors gracefully
- Be executable or importable by the test harness

### Database Integration
- Reuse the database connection from Milestone 1 (`/app/etl_pipeline.db`)
- Insert at least one log entry into the `log_entries` table to verify ETL functionality
- Ensure all required columns are populated (id will auto-increment)

### Validation
The tests will verify:
- `/app/log_parser.py` exists
- `/app/milestone2_done.txt` exists (created after log parsing completes)
- At least one row exists in the `log_entries` table
- Log entries persist through to Milestone 3
