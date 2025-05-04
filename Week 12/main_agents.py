import os
from agents import Agent, Runner, function_tool
import asyncio
from dotenv import load_dotenv
# handsoff agents
from web_scraper_agent import web_scraper_agent
from google_sheet_agent import google_sheet_agent
from sqlite_agent import SQLite_Table_Agent

# Load environment variables
load_dotenv()

api_key = os.getenv("OPEN_API_KEY")

model = "gpt-4o-mini"

# @function_tool
# def full_pipe(user_query:str, db_name: str, table_name: str, file_path:str):
#     # Step 1: Extract URLs from Google Sheet
#     urls_result = Runner.run_sync(google_sheet_agent, user_query)
#     urls = urls_result.final_output

#     # Step 2: Scrape company info from URLs
#     scrape_result = Runner.run_sync(web_scraper_agent, urls)
#     company_data = scrape_result.final_output
    
#      # Step 3: Insert company info into database
#     # Optionally, save company_data to file_path if needed
#     # with open(file_path, "w", encoding="utf-8") as f:
#     #     json.dump(company_data, f, indent=2)
#     db_result = Runner.run_sync(SQLite_Table_Agent, {
#         "tool": "insert_data",
#         "db_name": db_name,
#         "table_name": table_name,
#         "file_path": file_path
#     })
#     return f"Pipeline complete. DB result: {db_result.final_output}"
    
    
main_agent = Agent(
    name="Company Info Orchestrator",
    instructions="""
You are a smart orchestrator. For any workflow that involves more than one step 
(e.g., extracting URLs, scraping, and inserting into a database), 
Do not call other tools directly for multi-step workflows.
Otherwise, For single-step requests (e.g., "fetch all data from database"), call the appropriate tool directly.
You have access to the following tools:

1. **Google Sheet Agent**
   - Tool: `extract_Google_sheet()`
   - Gets a list of company URLs from a Google Sheet.

2. **Web Scraper Agent**
   - Tool: `web_scraper(urls: List[str]) -> List[Dict]`
   - Takes in a list of URLs and returns structured company data.

3. **SQLite Agent**
   - Tools:
     - `create_table_from_data(db_name: str, table_name: str, file_path: str)`
     - `insert_data(db_name: str, table_name: str, file_path: str)`
     - `fetch_data(query: str, db_name: str)`
     - `delete_table(query: str, user_id: int, db_name: str)`

Rules:
- If the user wants to extract URLs from a Google Sheet, use `extract_Google_sheet`.
- If URLs are extracted or provided, use `web_scraper` to get company data.
- If the user mentions a file (e.g., web.json) and database/table, call:
   1. `create_table_from_data` with db_name, table_name, file_path
   2. Then `insert_data` with the same args.

Always pass data between tools in memory unless the user explicitly mentions using a file (e.g., "load from web.json").

Goal: Fulfill the full user workflow in order. Do not stop after the first step. Only return the final result or a completion message.
""",
    model=model,
    tools=[
           google_sheet_agent.tools[0],  # or the correct reference to your tool
        web_scraper_agent.tools[0],
        *SQLite_Table_Agent.tools
        
        
           ],
    handoffs=[google_sheet_agent, web_scraper_agent, SQLite_Table_Agent]
)


async def main():
    
    print("Ask your company info questions (type 'exit' to quit):")
    while True:
        user_query = input("What do you want to do? ")
        if user_query.strip().lower() in {"exit", "quit"}:
            break
        info_result = await Runner.run(main_agent, user_query)
        print("Extracted company data:")
        print(info_result.final_output)

if __name__ == "__main__":
    asyncio.run(main()) 