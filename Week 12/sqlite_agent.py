import sqlite3
import os
from agents import Agent, Runner, function_tool
from typing import List, Dict, TypedDict
import asyncio
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

api_key = os.getenv("OPEN_API_KEY")

class CompanyRow(TypedDict):
    CompanyName: str
    Website: str
    Email: str
    Phone: str
    TypeofCompany: str
    Sports: str
    Location: str
    Country: str
    Notes: str

model = 'gpt-4o-mini'

def read_json_data(json_path: str) -> List[Dict[str, str]]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Flatten all 'listings' arrays into one list
    if isinstance(data, list):
        all_companies = []
        for entry in data:
            if "listings" in entry and isinstance(entry["listings"], list):
                all_companies.extend(entry["listings"])
        return all_companies
    return data

"""Get DB Connection"""
def get_connection(db_name: str) -> None:
    try:
        return sqlite3.connect(db_name)
    except Exception as e:
        return (f"Error: {e}")
        
"""Create a table"""
@function_tool
def create_table_from_data(db_name: str, table_name: str, file_path: str) -> str:
    data = read_json_data(file_path)
    if not data:
        return "No data provided."
    try:
        conn = get_connection(db_name)
        headers = list(data[0].keys())
        columns = ', '.join([f'"{col}" TEXT' for col in headers])
        create_table_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns});'
        with conn:
            conn.execute(create_table_sql)
        return f"Table '{table_name}' created with columns: {headers}"
    except Exception as e:
        return f"Error: {e}"

    
# insert_data to db  
@function_tool  
def insert_data(db_name: str, table_name: str,   file_path: str) -> str:
    data = read_json_data(file_path)
    if not data:
        return "No data to insert."
    try:
        conn = get_connection(db_name)
        headers = list(data[0].keys())
        # Quote column names
        quoted_headers = [f'"{h}"' for h in headers]
        placeholders = ', '.join(['?'] * len(headers))
        insert_sql = f'INSERT INTO "{table_name}" ({", ".join(quoted_headers)}) VALUES ({placeholders})'
        values = [tuple(d.get(h, "") for h in headers) for d in data]
        with conn:
            conn.executemany(insert_sql, values)
        return f"Inserted {len(values)} rows into '{table_name}'"
    except Exception as e:
        return f"Error: {e}"
    
"""Read table"""
@function_tool
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

@function_tool       
def delete_table(query: str, user_id: int, db_name: str):
    conn = get_connection(db_name)
    cursor = conn.cursor()

    try:
        with conn:
           conn.execute(query)   
           return f"Deleted user with ID {user_id} from '{db_name}'"
    except sqlite3.OperationalError as e:
        return(f"Error: {e}")
    finally:
        conn.close()      


SQLite_Table_Agent = Agent(
    name="SQLite Table Agent",
    handoff_description="Specialist agent for creating and managing tables in SQLite databases.",
    instructions="""
    You are a Python assistant for managing SQLite databases.
    You can:
    - Create tables from a list of dictionaries (each dictionary is a row, keys are columns)
    - Insert data into tables
    - Fetch data using SQL queries
    - Delete tables or rows

    Always print a clear success message after creating a table or inserting data.
    When fetching, return the results as a list of dictionaries, one per row, with column names as keys.
    If a field is missing or not available, use an empty string for that field.
    Return ONLY the list of dictionaries, with no explanation, no code, and no extra text.
    """,
    model=model,
    tools=[create_table_from_data, insert_data, fetch_data, delete_table],
)

"""For testing agents"""
# async def main():
  
#     print("Ask your company info questions (type 'exit' to quit):")
#     while True:
#         user_query = input("What do you want to do? ")
#         if user_query.strip().lower() in {"exit", "quit"}:
#             break
#         info_result = await Runner.run(SQLite_Table_Agent, user_query)
#         print("Extracted company data:")
#         print(info_result.final_output)
# #run the server
# if __name__ == "__main__":
#     asyncio.run(main())