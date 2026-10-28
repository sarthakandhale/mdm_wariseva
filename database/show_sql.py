import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "reuniteai_local.db")

def show_all_sql():
    if not os.path.exists(DB_PATH):
        print("Database file not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 80)
    print("                      REUNITEAI DATABASE - ALL SQL SCHEMAS                      ")
    print("=" * 80)

    # Get all table creation SQL statements
    tables = cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL ORDER BY name;").fetchall()
    
    print(f"\nFound {len(tables)} Tables:\n")
    for name, sql in tables:
        print(f"-- Table: {name}")
        print(sql.strip() + ";\n")

    conn.close()

if __name__ == "__main__":
    show_all_sql()
