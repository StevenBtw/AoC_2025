import duckdb
import os

def write_input_to_db():
    table_name = "banks"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "duck.db")
    input_path = os.path.join(script_dir, "input.txt")
    
    conn = duckdb.connect(db_path)
    
    conn.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.execute(f"CREATE TABLE {table_name} (line_number INTEGER, line_data VARCHAR)")
    
    with open(input_path, "r") as file:
        for line_num, line in enumerate(file, 1):
            line_data = line.strip()
            if line_data:
                conn.execute(f"INSERT INTO {table_name} VALUES (?, ?)", [line_num, line_data])
    
    conn.close()

if __name__ == "__main__":
    write_input_to_db()