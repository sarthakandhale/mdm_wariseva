import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), "reuniteai_local.db")

def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 65)
    print("   ReuniteAI – Interactive Terminal SQL Shell")
    print(f"   Connected to: {os.path.abspath(DB_PATH)}")
    print("   Type '.tables' to list tables, '.schema <table>' for schema,")
    print("   or enter any SQL command (e.g. SELECT * FROM users;). Type 'exit' to quit.")
    print("=" * 65)

    while True:
        try:
            query = input("\nSQL> ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit", "q"):
                print("Goodbye!")
                break
            
            if query.lower() == ".tables":
                tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
                print(f"\n--- Total Tables ({len(tables)}) ---")
                for i, t in enumerate(tables, 1):
                    count = cursor.execute(f"SELECT COUNT(*) FROM \"{t[0]}\"").fetchone()[0]
                    print(f"{i:2d}. {t[0]:<35} ({count} rows)")
                continue

            if query.lower().startswith(".schema"):
                parts = query.split()
                if len(parts) > 1:
                    tbl = parts[1]
                    res = cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?;", (tbl,)).fetchone()
                    if res and res[0]:
                        print(f"\nSchema for {tbl}:\n{res[0]}")
                    else:
                        print(f"Table '{tbl}' not found.")
                else:
                    schemas = cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';").fetchall()
                    for s in schemas:
                        if s[0]:
                            print(f"{s[0]}\n")
                continue

            cursor.execute(query)
            if query.strip().upper().startswith("SELECT") or query.strip().upper().startswith("PRAGMA") or query.strip().upper().startswith("EXPLAIN"):
                rows = cursor.fetchall()
                colnames = [desc[0] for desc in cursor.description] if cursor.description else []
                print("\n" + " | ".join(colnames))
                print("-" * 65)
                for r in rows[:50]:
                    print(" | ".join(str(val) for val in r))
                print(f"\n({len(rows)} rows returned)")
            else:
                conn.commit()
                print(f"Query executed successfully. ({cursor.rowcount} rows affected)")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"SQL Error: {e}")

    conn.close()

if __name__ == "__main__":
    main()
