# Multi agents using OpenAI SDK with SQLite Application

This project provides three agents to fetch data from Google Sheets, web Scraping, and implement SQLite with OpenAI's GPT model, OpenAI SDK.

## Setup


1. Install the required libraries:
    
    pip install -r requirements.txt
Before running the program, users should have Google Sheets API, OpenAI API, and chromedriver.

## Files Overview

### 1. `main_agents.py`
Using the main agent to manage other agents with handsoff. 

### 2. `google_sheet_agent.py`
Using Google sheet API to fetch data from Google Sheets. 

### 3. `web_scraper_agent.py`
Web Scraper agent to manage scraper.py

### 4. `sqlite_agent.py`
SQLite agent can create table, insert data, fetch data, and delete table. 

### 5. `scraper.py`
Using ChatGPT to fetch data from BeautifulSoup. 

#### How to Run:
Users can use examples at the below 
```bash
python main_agents.py

fetch all URLs from the google drive

web scraping these urls ['http://draftkings.com', 'http://leagueapps.com', 'playsight.com', 'proteusmotion.com', 'rapsodo.com', 'geniussports.com', 'hudl.com', 'shottracker.com', 'coachmeplus.com', 'itsovertime.com']

create a table. table name is sample1, database name is SAMPLE.db, file path is web.json

insert data. table name is sample1, database name is SAMPLE.db, file path is web.json

fetch all data from sample1 in SAMPLE.db


NOTE: USERS must provide correct table name, database name, and which columns or rows they want to fetch data because this application is in case sensitive.


You can use the prompt below to do the serial communicate with each agents
Users also can prompt simple prompt to do a specific work with one agent.

Step 1: Get URLs from Google sheet and pass them to the web_scraper tool of the web scraper agent.Step 2: 
Load data from web.json and then create a database name as SAMPLE.db and table name as sample1. step 3: insert data to a database named SAMPLE.db and table name sample1.