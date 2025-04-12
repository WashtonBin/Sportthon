# Sportthon Intern
Week 6: Web Scraper can scrap most of the websites with selenium and ChatGPT. I scraped Nike Offical website. It returns location, the name of staffs, the company culture, etc. Users can modify the json files to scrap data what they want.

Week 9: Video Editor can edit highlights based on Gemini flash 2.0 analyzing video features and Moviepy. Beacause of the limitation and correctess of Gemini output, we can generate a less 45 mins video. Note: I tested movies, animes, and sports games. Gemini can not work on sports games. I assume that Gemini is not able to distinguish between the important event in a sport game even though I prompted "focusing on basketball shots". Gemini return an empty list.

Week 10: RAG Generator can fetch data from "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi" a medical article website. And then I provide two options to store data including Pinecone assistant and Pinecone database. If you choose Pinecone assistant, this agent automatically embed data and give you an answer. If you pick pinecone database, ChatGPT will embed data and then store data to the database.
