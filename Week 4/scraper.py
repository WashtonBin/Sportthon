import os
import time
import re
import json
from typing import List, Type

import pandas as pd
from bs4 import BeautifulSoup
from pydantic import BaseModel, create_model
import html2text
import tiktoken

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from openai import OpenAI
from openpyxl import load_workbook

load_dotenv()

# Set up the Chrome WebDriver options
def setup_selenium():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service(r"./chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def fetch_html_selenium(url):
    driver = setup_selenium()
    try:
        driver.get(url)
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        html = driver.page_source
        # print("Fetched HTML:", html[:500])  # Debug print
        return html
    finally:
        driver.quit()

def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for element in soup.find_all(['header', 'footer']):
        element.decompose()
    return str(soup)

def html_to_markdown_with_readability(html_content):
    cleaned_html = clean_html(html_content)
    markdown_converter = html2text.HTML2Text()
    markdown_converter.ignore_links = False
    markdown_content = markdown_converter.handle(cleaned_html)
    # print("Converted Markdown:", markdown_content[:500])  # Debug print
    return markdown_content

pricing = {
    "gpt-4o-mini": {
        "input": 0.150 / 1_000_000,
        "output": 0.600 / 1_000_000,
    },
    "gpt-4o-2024-08-06": {
        "input": 2.5 / 1_000_000,
        "output": 10 / 1_000_000,
    },
    "gpt-4o": {
        "input": 1.0 / 1_000_000,  # Example pricing, update with actual values
        "output": 4.0 / 1_000_000,  # Example pricing, update with actual values
    },
}

model_used = "gpt-4o-mini"  # Default model, update as needed


def remove_urls_from_file(file_path):
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    base, ext = os.path.splitext(file_path)
    new_file_path = f"{base}_cleaned{ext}"
    with open(file_path, 'r', encoding='utf-8') as file:
        markdown_content = file.read()
    cleaned_content = re.sub(url_pattern, '', markdown_content)
    with open(new_file_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_content)
    print(f"Cleaned file saved as: {new_file_path}")
    return cleaned_content

def create_dynamic_listing_model(field_names: List[str]) -> Type[BaseModel]:
    field_definitions = {field: (str, ...) for field in field_names}
    return create_model('DynamicListingModel', **field_definitions)

def create_listings_container_model(listing_model: Type[BaseModel]):
    return create_model('DynamicListingsContainer', listings=(List[listing_model], ...))

def trim_to_token_limit(text, model, max_tokens=200000):
    encoder = tiktoken.encoding_for_model(model)
    tokens = encoder.encode(text)
    if len(tokens) > max_tokens:
        trimmed_text = encoder.decode(tokens[:max_tokens])
        return trimmed_text
    return text

def format_data(data, DynamicListingsContainer):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    system_message = """You are an intelligent text extraction and conversion assistant. Your task is to extract structured information 
                        from the given text and convert it into a pure JSON format. The JSON should contain only the structured data extracted from the text, 
                        with no additional commentary, explanations, or extraneous information. 
                        You could encounter cases where you can't find the data of the fields you have to extract or the data will be in a foreign language.
                        Please process the following text and provide the output in pure JSON format with no words before or after the JSON:"""
    user_message = f"Extract the following information from the provided text:\nPage content:\n\n{data}"
    # print("User Message:", user_message)  # Debug print
    completion = client.beta.chat.completions.parse(
        model=model_used,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        response_format=DynamicListingsContainer
    )
    # print("Completion:", completion)  # Debug print
    if completion.choices and completion.choices[0].message.parsed:
        # print("Formatted Data:", completion.choices[0].message.parsed)  # Debug print
        return completion.choices[0].message.parsed
    else:
        # print("No data extracted")  # Debug print
        return DynamicListingsContainer(listings=[])

def save_formatted_data(formatted_data, file_name, output_folder='output'):
    os.makedirs(output_folder, exist_ok=True)
    formatted_data_dict = formatted_data.model_dump() if hasattr(formatted_data, 'model_dump') else formatted_data
    json_output_path = os.path.join(output_folder, f'sorted_data_{file_name}.json')
    excel_output_path = os.path.join(output_folder, f'sorted_data_{file_name}.xlsx')
    
    # Read existing data from the JSON file if it exists
    if os.path.exists(json_output_path):
        with open(json_output_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    # Append new data to the existing data
    if isinstance(existing_data, list):
        existing_data.append(formatted_data_dict)
    elif isinstance(existing_data, dict):
        for key, value in formatted_data_dict.items():
            if key in existing_data:
                if isinstance(existing_data[key], list):
                    existing_data[key].extend(value)
                else:
                    existing_data[key] = value
            else:
                existing_data[key] = value
    else:
        raise ValueError("Existing data is neither a dictionary nor a list, cannot append new data")

    # Write the updated data back to the JSON file
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=4)
    print(f"Formatted data saved to JSON at {json_output_path}")



def calculate_price(input_text, output_text, model=model_used):
    encoder = tiktoken.encoding_for_model(model)
    input_token_count = len(encoder.encode(input_text))
    output_token_count = len(encoder.encode(output_text))
    input_cost = input_token_count * pricing[model]["input"]
    output_cost = output_token_count * pricing[model]["output"]
    total_cost = input_cost + output_cost
    return input_token_count, output_token_count, total_cost


def read_from_json(path, key):
    try:
        with open(path, 'r') as file:
            content = json.load(file)
            return content[key]
    except FileNotFoundError:
        print("The file does not exist.")
    except KeyError:
        print(f"The field '{key}' does not exist in the JSON file.")
    except json.JSONDecodeError:
        print("Error decoding JSON.")
    except Exception as e:
        print(f"An error occurred: {e}")          
            
def articles():
    output_folder = r'output\articles'
    urls = read_from_json('urls.json', 'sportsnews')
    fields = read_from_json('fields.json', 'sportsnews')
    for url in urls: 
        try:
            raw_html = fetch_html_selenium(url)
            markdown = html_to_markdown_with_readability(raw_html)
            DynamicListingModel = create_dynamic_listing_model(fields)
            DynamicListingsContainer = create_listings_container_model(DynamicListingModel)
            formatted_data = format_data(markdown, DynamicListingsContainer)
            
            # Access the 'listings' attribute of the formatted_data object
            listings = formatted_data.listings
            if listings:
                # Access the attribute of the first listing object
                file_name = getattr(listings[0], 'the Sports Category of the article', 'default_filename')
                save_formatted_data(formatted_data, file_name, output_folder)
                formatted_data_text = json.dumps(formatted_data.model_dump())
                input_tokens, output_tokens, total_cost = calculate_price(markdown, formatted_data_text, model=model_used)
                print(f"Input token count: {input_tokens}")
                print(f"Output token count: {output_tokens}")
                print(f"Estimated total cost: ${total_cost:.4f}")
            else:
                print("No listings found in the formatted data.")
        except Exception as e:
            print(f"An error occurred: {e}")
            
            

def jobs():
    output_folder = r'output\jobs'
    urls = read_from_json('urls.json', 'jobs')
    fields = read_from_json('fields.json', 'jobs')
    for url in urls: 
        try:
            raw_html = fetch_html_selenium(url)
            markdown = html_to_markdown_with_readability(raw_html)
            DynamicListingModel = create_dynamic_listing_model(fields)
            DynamicListingsContainer = create_listings_container_model(DynamicListingModel)
            formatted_data = format_data(markdown, DynamicListingsContainer)
            file_name = 'jobs'
            save_formatted_data(formatted_data, file_name, output_folder)
            formatted_data_text = json.dumps(formatted_data.model_dump())
            input_tokens, output_tokens, total_cost = calculate_price(markdown, formatted_data_text, model=model_used)
            print(f"Input token count: {input_tokens}")
            print(f"Output token count: {output_tokens}")
            print(f"Estimated total cost: ${total_cost:.4f}")
        except Exception as e:
            print(f"An error occurred: {e}")
            
            
if __name__ == "__main__":
    articles()
    # jobs()
