import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), "reuniteai_local.db")

# Force UTF-8 output on stdout for Windows terminal
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    if not os.path.exists(DB_PATH):
        print("Database file not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;").fetchall()
    
    print("=" * 80)
    print("                      REUNITEAI DATABASE CONTENTS SUMMARY                       ")
    print("=" * 80)
    print(f"Total Tables: {len(tables)}\n")

    for t in tables:
        tbl_name = t[0]
        count = cursor.execute(f"SELECT COUNT(*) FROM \"{tbl_name}\"").fetchone()[0]
        if count > 0:
            print(f"\n==================== TABLE: {tbl_name} ({count} rows) ====================")
            cursor.execute(f"SELECT * FROM \"{tbl_name}\" LIMIT 5;")
            col_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            header = " | ".join(col_names)
            print(header)
            print("-" * min(len(header), 120))
            
            for row in rows:
                row_str = " | ".join(str(val) if val is not None else "NULL" for val in row)
                print(row_str[:200])

    conn.close()

if __name__ == "__main__":
    main()
