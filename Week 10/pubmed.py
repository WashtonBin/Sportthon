import requests
from xml.etree import ElementTree
import os
import re
import json

def fetch_pmc_articles(category, max_results=10):
    """
    Fetch articles from PubMed Central (PMC) based on a search query.

    Args:
        query (str): The search term for PMC.
        max_results (int): Maximum number of articles to fetch.

    Returns:
        list: A list of dictionaries containing article details.
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    details_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    # Step 1: Search for articles in PMC
    search_params = {
        "db": "pmc",  # Use the PMC database
        "term": category,
        "retmax": max_results,
        "retmode": "xml"
    }
    search_response = requests.get(base_url, params=search_params)
    search_response.raise_for_status()

    # Parse the search results to get PMC IDs
    search_tree = ElementTree.fromstring(search_response.content)
    pmc_ids = [id_elem.text for id_elem in search_tree.findall(".//Id")]

    if not pmc_ids:
        return []

    # Step 2: Fetch article details from PMC
    fetch_params = {
        "db": "pmc",  # Use the PMC database
        "id": ",".join(pmc_ids),
        "retmode": "xml"
    }
    fetch_response = requests.get(details_url, params=fetch_params)
    fetch_response.raise_for_status()

    # Parse the article details
    articles = []
    fetch_tree = ElementTree.fromstring(fetch_response.content)
    for article in fetch_tree.findall(".//article"):
        title = article.findtext(".//article-title", default="No Title")
        abstract = article.findtext(".//abstract", default="No Abstract")
        journal = article.findtext(".//journal-title", default="No Journal")
        pub_date = article.findtext(".//pub-date/year", default="No Date")
        authors = [
            f"{author.findtext('surname', '')} {author.findtext('given-names', '')}".strip()
            for author in article.findall(".//contrib[@contrib-type='author']")
        ]

        # Attempt to fetch full text from <body> or <sec> tags
        full_text = ""
        body = article.find(".//body")
        if body is not None:
            full_text = "".join(body.itertext()).strip()
            articles.append({
            "title": title,
            "abstract": abstract,
            "journal": journal,
            "publication_date": pub_date,
            "authors": authors,
            "full_text": full_text
        })
        else:
            full_text = "Full text not available." 

    return articles

def save_files_json(articles):
    path = "./medical_articles"
    article_number = []
    # Ensure the "./medical_files" directory exists
    os.makedirs(path, exist_ok=True)
    for idx, article in enumerate(articles, start=1):
        
        # Sanitize the title to create a valid filename
        safe_title = re.sub(r'[\\/*?:"<>|]', "_", article['title'])
        
          # Create a JSON object for the article
        article_json = {
            "idx": idx,
            "title": article['title'],
            "abstract": article['abstract'],
            "journal": article['journal'],
            "publication_date": article['publication_date'],
            "authors": article['authors'],
            "content": article['full_text']
        }
        
        # Save the JSON object to a file
        json_file_path = f"{path}/{safe_title}.json"
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(article_json, json_file, ensure_ascii=False, indent=4)
        result = (f"Article {idx} saved to {json_file_path}")
        article_number.append(result)
    return article_number 
        
def main(category):
    articles = fetch_pmc_articles(category, max_results=20)  # Adjust max_results as needed
    return save_files_json(articles)
    