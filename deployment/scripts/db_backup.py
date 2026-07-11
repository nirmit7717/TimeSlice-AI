import os
import sys
import sqlite3
import zipfile
import argparse
from datetime import datetime

def backup_db(db_path: str, backup_dir: str) -> None:
    """
    Performs atomic, online backups of SQLite databases and compresses them.
    """
    if not os.path.exists(db_path):
        print(f"Error: Database source file not found at '{db_path}'")
        sys.exit(1)

    # 1. Create target directory
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_backup = os.path.join(backup_dir, f"temp_timeslice_{timestamp}.db")
    compressed_backup = os.path.join(backup_dir, f"backup_timeslice_{timestamp}.zip")

    try:
        # 2. Perform atomic backup using SQLite backup API
        print(f"Starting atomic database snapshot copy from '{db_path}'...")
        src_conn = sqlite3.connect(db_path)
        dest_conn = sqlite3.connect(temp_backup)
        
        with dest_conn:
            src_conn.backup(dest_conn)
            
        dest_conn.close()
        src_conn.close()
        print("Database copy completed successfully.")

        # 3. Compress snapshot
        print(f"Compressing database backup into '{compressed_backup}'...")
        with zipfile.ZipFile(compressed_backup, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(temp_backup, arcname=os.path.basename(db_path))
            
        # 4. Remove temp uncompressed copy
        os.remove(temp_backup)
        print(f"Backup created successfully: {compressed_backup}")
        
    except Exception as e:
        if os.path.exists(temp_backup):
            os.remove(temp_backup)
        print(f"Database backup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TimeSlice Local SQLite DB Backup Utility")
    parser.add_argument("--db-path", default="w:/Projects Antigravity/TimeSlice AI/timeslice_local.db", help="Path to SQLite DB file")
    parser.add_argument("--dest", default="w:/Projects Antigravity/TimeSlice AI/backups", help="Target backup folder path")
    
    args = parser.parse_args()
    backup_db(args.db_path, args.dest)
