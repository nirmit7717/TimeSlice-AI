import os
import sys
import zipfile
import shutil
import argparse

def restore_db(backup_file: str, db_path: str) -> None:
    """
    Restores SQLite database from a compressed backup ZIP file.
    """
    if not os.path.exists(backup_file):
        print(f"Error: Backup file not found at '{backup_file}'")
        sys.exit(1)

    temp_dir = os.path.join(os.path.dirname(backup_file), "temp_restore")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # 1. Unzip the archive
        print(f"Extracting backup archive '{backup_file}'...")
        with zipfile.ZipFile(backup_file, "r") as zipf:
            zipf.extractall(temp_dir)
            
        extracted_files = os.listdir(temp_dir)
        if not extracted_files:
            raise ValueError("Backup archive is empty")
            
        extracted_db = os.path.join(temp_dir, extracted_files[0])

        # 2. Overwrite target database file safely
        print(f"Restoring database to target location '{db_path}'...")
        
        # Ensure parent folder of target DB path exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        shutil.copy2(extracted_db, db_path)
        print("Database restored successfully.")
        
    except Exception as e:
        print(f"Database restoration failed: {str(e)}")
        sys.exit(1)
        
    finally:
        # Cleanup temporary extraction directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TimeSlice Local SQLite DB Restore Utility")
    parser.add_argument("--backup-file", required=True, help="Path to compressed ZIP backup file")
    parser.add_argument("--db-path", default="w:/Projects Antigravity/TimeSlice AI/timeslice_local.db", help="Target SQLite DB path to overwrite")
    
    args = parser.parse_args()
    restore_db(args.backup_file, args.db_path)
