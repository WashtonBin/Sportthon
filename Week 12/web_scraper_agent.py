from scraper import fetch_html_selenium, html_to_markdown_with_readability ,create_dynamic_listing_model, create_listings_container_model, format_data, save_formatted_data
from agents import Agent, Runner, function_tool
import asyncio

from google_sheet_agent import google_sheet_agent, extract_Google_sheet

model = 'gpt-4o-mini'
@function_tool
def web_scraper(urls: list[str]):
    # Hardcoded fields
    fields = [
        "CompanyName",
        "Website",
        "Email",
        "Phone",
        "TypeofCompany",
        "Sports",
        "Location",
        "Country",
        "Notes"
    ]
    for url in urls:
        try:
            print(url)
            print("Loaded URLs:", url)  # Debug print
            raw_html = fetch_html_selenium(url)
            markdown = html_to_markdown_with_readability(raw_html)
            DynamicListingModel = create_dynamic_listing_model(fields)
            DynamicListingsContainer = create_listings_container_model(DynamicListingModel)
            formatted_data = format_data(markdown, DynamicListingsContainer)
            file_name = "web.json"
            save_formatted_data(formatted_data, file_name)
        
        except Exception as e:
            print(f"An error occurred: {e}")
    return formatted_data

web_scraper_agent = Agent(
    name="Web Scraper",
    handoff_description="Specialist agent for web scraping",
    instructions="""
                You are a Python assistant that extracts structured company information from a list of provided URLs.
                
                
                Using web_scraper to return the extracted data as a list of dictionaries, one per company, with each dictionary containing the above fields as keys.
                If a field is missing or not available, use an empty string for that field.
                Return ONLY the list of dictionaries, with no explanation, no code, and no extra text.
                
                """,
    model=model,
    tools=[web_scraper]
)

"""For testing agents"""
# main_agent = Agent(
#     name="Company Info Orchestrator",
#     instructions="""
#             You are an orchestrator agent. 
#             If the user asks for company information from a Google Sheet, first hand off to the Google Sheet Extractor agent to get the URLs using the extract_Google_sheet tool, then hand off to the Web Scraper agent to extract company information for those URLs using the company_information tool. 
#             If the user provides URLs directly, use the Web Scraper agent. 
#             Return ONLY the final list of company information dictionaries.
#                 """,
#     model=model,
#     handoffs=[web_scraper_agent, google_sheet_agent]
# )
# async def main():
    
#     print("Ask your company info questions (type 'exit' to quit):")
#     while True:
#         user_query = input("What do you want to do? ")
#         if user_query.strip().lower() in {"exit", "quit"}:
#             break
#         info_result = await Runner.run(main_agent, user_query)
#         print("Extracted company data:")
#         print(info_result.final_output)

# if __name__ == "__main__":
#     asyncio.run(main()) 