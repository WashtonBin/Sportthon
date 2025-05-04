import gspread
from google.oauth2.service_account import Credentials
from agents import Agent, Runner, function_tool

from dotenv import load_dotenv
import os

import asyncio
import json
from typing import List

# Load environment variables
load_dotenv()

api_key = os.getenv("OPEN_API_KEY")
google_sheet_url = os.getenv("GOOGLE_SHEET_URL")
model = 'gpt-4o-mini'

@function_tool
def extract_Google_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets"
    ]

    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)

    sheet_url = google_sheet_url
    sh = client.open_by_url(sheet_url)

    worksheet = sh.sheet1

    values_list = worksheet.get_all_values()
    return values_list


google_sheet_agent = Agent(
    name="Google Sheet Extractor",
    handoff_description="Specialist agent for fetch data from Google Sheets",
    instructions="""
                    You are a Python assistant that extracts specific columns from a Google Sheet.
                    Given the following table data as a list of lists (first row is the header), 
                    Using extract_Google_sheet tool to extract and return ONLY a Python list of all non-empty cell from a specific column, 
                    excluding any that are empty or 'Not Available'. 
                    Return ONLY the list, with no explanation, no code, and no extra text. 
                    Here is the data:\n\n
                    """,
    model=model,
    tools=[extract_Google_sheet]
)


"""For testing agents"""
# async def main():
#     query = "I want to extract all urls from this sheet."
#     result = await Runner.run(google_sheet_agent, query)
#     print("Extracted emails:")
#     print(result.final_output)


# if __name__ == "__main__":
#     asyncio.run(main())