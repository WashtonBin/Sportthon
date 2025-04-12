import os
from dotenv import load_dotenv
import openai
from pymongo import MongoClient
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_core.documents import Document
import sys

load_dotenv()

print(f"Current working directory: {os.getcwd()}")

mongo_key = os.getenv('MONGODB_KEY')
openai.api_key = os.getenv('OPENAI_API_KEY')

client = MongoClient(mongo_key)
dbName = "Nike_db"
CollectionName = "collection_of_text_blobs"
collection = client[dbName][CollectionName]

# Use absolute path to the sample_files directory
base_dir = os.path.abspath(os.path.dirname(__file__))
sample_files_path = os.path.join(base_dir, 'Nike')
print(f"Looking for files in: {sample_files_path}")

# Check for files in directory
txt_files = [f for f in os.listdir(sample_files_path) if f.endswith(('.txt', 'md'))]
print(f"Found {len(txt_files)} text files: {txt_files}")

# Manual document loading
documents = []
try:
    for file_name in txt_files:
        file_path = os.path.join(sample_files_path, file_name)
        print(f"Loading file: {file_name}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                # Create Document object manually
                doc = Document(
                    page_content=text,
                    metadata={"source": file_path}
                )
                documents.append(doc)
                print(f"Successfully loaded {file_name} - {len(text)} characters")
        except Exception as file_error:
            print(f"Error with file {file_name}: {file_error}")
    
    print(f"Successfully loaded {len(documents)} documents")
    
    # Process with embeddings and vector store
    if documents:
        embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)
        print("Initialized embedding model")
        
        # Process documents one by one to isolate issues
        for i, doc in enumerate(documents):
            try:
                print(f"Processing document {i+1}/{len(documents)}: {doc.metadata['source']}")
                # Creat   single_doe vector store with just this document
                c_store = MongoDBAtlasVectorSearch.from_documents(
                    [doc], embeddings, collection=collection
                )
                print(f"Document {i+1} processed successfully")
            except Exception as doc_error:
                print(f"Error processing document {i+1}: {doc_error}")
                import traceback
                traceback.print_exc()
        
        print("All documents processed")
    else:
        print("No documents were loaded, cannot create vector store")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Always close your MongoDB connection
    client.close()
    print("MongoDB connection closed")


