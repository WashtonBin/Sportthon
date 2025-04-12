import os
from dotenv import load_dotenv
import openai
from pymongo import MongoClient
from langchain_openai import OpenAIEmbeddings, ChatOpenAI  # Updated import
from langchain_community.vectorstores import MongoDBAtlasVectorSearch  # Updated import
from langchain_community.document_loaders import DirectoryLoader  # Updated import
from langchain.chains import RetrievalQA  # Correct import for RetrievalQA
import gradio as gr
from gradio.themes.base import Base


import tiktoken

load_dotenv()


mongo_key = os.getenv('MONGODB_KEY')
openai.api_key = os.getenv('OPENAI_API_KEY')

    
client = MongoClient(mongo_key)
dbName = "Nike_db"
CollectionName = "collection_of_text_blobs"
collection = client[dbName][CollectionName]

embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)

vectorStore = MongoDBAtlasVectorSearch(collection, embeddings,  index_name="knn")

    


def query_data(query):
    try:
        # Debug: Check if collection has documents
        doc_count = collection.count_documents({})
        print(f"Found {doc_count} documents in collection")
        
        docs = vectorStore.similarity_search(query, k=1)
        if not docs:
            return "No matching documents found."  # SINGLE STRING
        
        # Get the document content
        doc_content = docs[0].page_content
        
        # Truncate to approximately 12K tokens
        enc = tiktoken.get_encoding("cl100k_base")
        tokens = enc.encode(doc_content)
        if len(tokens) > 12000:
            tokens = tokens[:12000]
            doc_content = enc.decode(tokens)
        
        llm = ChatOpenAI(openai_api_key=openai.api_key, temperature=0)
        retriever = vectorStore.as_retriever(search_kwargs={"k": 1})
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)
        retriever_output = qa.run(query)
        
        return retriever_output  # SINGLE STRING
    except Exception as e:
        return f"Error: {str(e)}"  # SINGLE STRING
    
  



with gr.Blocks(theme=Base(), title="Question Answering App using Vector + RAG") as demo:
    gr.Markdown(
    """#Question Answering App using Atlas Vector Search + RAG Architecture
    """
    )
    textbox = gr.Textbox(label="Enter your Question:")
    with gr.Row():
        button = gr.Button("Submit", variant="primary")
    
    output = gr.Textbox(lines=1, max_lines=10, label="AI Response:")
    
    button.click(query_data, textbox, outputs=[output])
    
demo.launch(share=True)


