from mcp.server.fastmcp import FastMCP
import requests
import sqlite3
import csv
import os
mcp = FastMCP("SQLite3 Server")

"""Get DB Connection"""
@mcp.tool()
def get_connection(db_name: str) -> None:
    try:
        return sqlite3.connect(db_name)
    except Exception as e:
        return (f"Error: {e}")
        
"""Create a table from CSV"""
@mcp.tool()
def create_table_from_csv(db_name: str, table_name: str, csv_file: str) -> str:
    try:
        conn = get_connection(db_name)
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)

            # Generate CREATE TABLE SQL
            columns = ', '.join([f'"{col}" TEXT' for col in headers])
            create_table_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns});'

            with conn:
                conn.execute(create_table_sql)
        return (f"Table '{table_name}' created with columns: {headers}")
    except Exception as e:
        return (f"Error: {e}")

"""Load a CSV to the table"""
@mcp.tool()
def load_csv_to_table(db_name: str, table_name: str, csv_file: str) -> str:
    try:
        db_path = os.path.join(os.path.dirname(__file__), db_name)
        conn = get_connection(db_path)
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)
            data = list(reader)

        placeholders = ', '.join(['?'] * len(headers))
        insert_sql = f'INSERT INTO "{table_name}" VALUES ({placeholders})'

        with conn:
            conn.executemany(insert_sql, data)
            return (f"Inserted {len(data)} rows into '{table_name}'")
    except Exception as e:
        return (f"Error: {e}")
    

"""Read table"""
@mcp.tool()
def fetch_data(query: str, db_name: str) -> list[str]:
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except sqlite3.OperationalError as e:
        return [f"Error: {e}"]
    finally:
        conn.close()
        
@mcp.tool()
def delete(query: str, user_id: int, db_name: str):
    conn = get_connection(db_name)
    cursor = conn.cursor()

    try:
        with conn:
           conn.execute(query)   

    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
    finally:
        conn.close()      

#run the server
if __name__ == "__main__":
    mcp.run()