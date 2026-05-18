## Milestone 3: ETL Pipeline with FFmpeg

### Objective
Complete the ETL pipeline by:
1. Integrating FFmpeg for media file processing
2. Extracting media metadata (duration, bitrate, format, codec)
3. Linking media metadata to log entries in the database
4. Creating an end-to-end ETL pipeline that extracts, transforms, and loads data
5. Creating a marker file to indicate successful completion

### Required Artifacts
1. **media_processor.py** - A Python module in `/app` that implements media processing functionality
2. **milestone3_done.txt** - A marker file in `/app` created after milestone 3 completes
3. **media/ directory** - A directory at `/app/media` containing sample media files for processing
4. **Persisted artifacts from Milestones 1 and 2**:
   - `/app/hello.txt` (from Milestone 1)
   - `/app/milestone2_done.txt` (from Milestone 2)

### media_processor.py Implementation
The module must:
- Have a function or class that processes media files
- Extract metadata: duration, format, bitrate (using FFmpeg-style extraction)
- Insert processed metadata into the `media_metadata` table with foreign keys to `log_entries`
- Link media files to their corresponding log entries
- Handle multiple media formats
- Be executable or importable by the test harness

### Sample Media Files
- Create at least one sample media file in `/app/media/` for processing
- Files should be processable by FFmpeg or FFmpeg-compatible tools
- Metadata should be extractable and stored in the database

### Database Integration
- Reuse the database connection from Milestones 1 and 2
- Insert at least one media metadata entry into `media_metadata` table with proper foreign key references
- Preserve all log entries from Milestone 2
- Maintain foreign key relationships between tables

### Validation
The tests will verify:
- `/app/hello.txt` still exists from Milestone 1
- `/app/milestone2_done.txt` still exists from Milestone 2
- `/app/milestone3_done.txt` exists (created after media processing completes)
- `/app/media_processor.py` exists
- `/app/media/` directory exists with at least one media file
- At least one row exists in `media_metadata` table
- At least one row still exists in `log_entries` table (from Milestone 2)
- Foreign key relationships between tables are maintained
- Complete ETL pipeline has data in both tables
