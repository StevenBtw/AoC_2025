import duckdb
import os

def setup_database():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "duck.db")
    conn = duckdb.connect(db_path)
    conn.close()
    print(f"Database {db_path} created successfully")

if __name__ == "__main__":
    setup_database()