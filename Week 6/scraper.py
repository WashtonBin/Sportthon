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
    print("Converted Markdown:", markdown_content)  # Debug print
    return markdown_content

def save_raw_data(raw_data, timestamp, output_folder='output'):
    os.makedirs(output_folder, exist_ok=True)
    raw_output_path = os.path.join(output_folder, f'rawData_{timestamp}.md')
    with open(raw_output_path, 'w', encoding='utf-8') as f:
        f.write(raw_data)
    return raw_output_path 



def remove_urls_from_file(file_path):
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    base, ext = os.path.splitext(file_path)
    # new_file_path = f"{base}_cleaned{ext}"
    with open(file_path, 'r', encoding='utf-8') as file:
        markdown_content = file.read()
    cleaned_content = re.sub(url_pattern, '', markdown_content)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_content)
    return cleaned_content



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
            
def scraping(company):
    urls = read_from_json('urls.json', company)
    for url in urls: 
        try:
             # Generate a unique identifier from the URL
            url_id = url.replace('https://', '').replace('http://', '').split('/')[0]
            timestamp = f"{url_id}_{time.strftime('%Y%m%d_%H%M%S')}"
            raw_html = fetch_html_selenium(url)
            markdown = html_to_markdown_with_readability(raw_html)
            raw_data_path = save_raw_data(markdown, timestamp, output_folder=company)
            remove_urls_from_file(raw_data_path)
        except Exception as e:
            print(f"An error occurred: {e}")
            
            
            
            
if __name__ == "__main__":
    
    scraping("Nike")
  
