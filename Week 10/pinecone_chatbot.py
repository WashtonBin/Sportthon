from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import JSONLoader
import os
from openai import OpenAI
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec


load_dotenv()
OPENAI_API_KEY   = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV     = os.getenv('PINECONE_ENVIRONMENT')


openai_client = OpenAI(api_key=OPENAI_API_KEY)
pc            = Pinecone(api_key=PINECONE_API_KEY)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)


def load_data(file_path, index_name):
    if not index_name in pc.list_indexes().names():
        create_db(index_name)
        
    loader = JSONLoader(
        file_path=file_path,
        jq_schema=r'''
          {
            rating: .rating,
            itle: .title,
            text: .text,
            asin: .asin,
            parent_asin: .parent_asin,
            user_id: .user_id, 
            timestamp: .timestamp, 
            helpful_vote: .helpful_vote, 
            verified_purchase: .verified_purchase
          }
        ''',
        text_content=False,  # important, since we're returning an object
        json_lines=True
    )

    docs = loader.load()
    #debug loader
    # print(docs)

    # #Split out documents into chunks
    text_splitter = RecursiveCharacterTextSplitter()
    split_docs = text_splitter.split_documents(docs)

    PineconeVectorStore.from_documents(split_docs, embeddings, index_name=index_name)

    #debug print data in pinecone
    # similar_docs = vectorstore.similarity_search(query)
    # print (similar_docs)
    return (f"{file_path} loaded to {index_name} successfully.")
    
        
        





def ask_query(query, index_name):
    if index_name in pc.list_indexes().names():
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0
        )

        vectorstore = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embeddings)
        retriever=vectorstore.as_retriever()

        system_prompt = (
            "Use the given context to answer the question. "
            "If you don't know the answer, say you don't know. "
            "Use three sentence maximum and keep the answer concise. "
            "Context: {context}"
        )
     
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", f"{query}"),
            ]
        )

        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        chain = create_retrieval_chain(retriever, question_answer_chain)

        result = chain.invoke({"input": query})
        # Format the output as a dictionary
        response = {
            "query": query,
            "answer": result["answer"]
        }

        # return the formatted response
        return response
    else:
        return (f"no {index_name} exists")


def delete_db(index_name):
    if index_name in pc.list_indexes().names():
         pc.delete_index(index_name)
         return (f"🗑️  Deleted existing index '{index_name}'")
    else:
        return (f"no {index_name} exists")

def create_db(index_name):
    if not index_name in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=1536,             # matches text-embedding-ada-002
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        return (f"✅ Created index '{index_name}' (dim=1536)")
    else:
        return (f"{index_name} has already existed")


 
# if __name__ == "__main__":
#     index_name = "amazonreviewlarge"
#     file_path = "./amazon_review/Beauty.jsonl"
    # query = "These reviews is positive or negative?"
    # print(delete_db(index_name))
    # print(create_db(index_name))
    # load_data(file_path, index_name)
    # print(ask_query(query, index_name))