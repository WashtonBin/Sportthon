import os
from dotenv import load_dotenv
from pinecone import Pinecone
from pinecone_plugins.assistant.models.chat import Message
import json
import time
import tempfile  

load_dotenv()

pinecone_key = os.getenv('PINECONE_API_KEY')
pc = Pinecone(api_key=pinecone_key)

#create an assistant
def create_assistant(assistant_name="example"):
    if not check_assistant_name(assistant_name):
        assistant = pc.assistant.create_assistant(
            assistant_name=assistant_name,
            instructions="Use American English for spell and grammar",
            region="us",
            timeout=30
    )
        print(f"Create assistant_name {assistant_name} successfully.")
    else:
        print(f"{assistant_name} has already existed.")
    
#get an assistant   
def upload_files(file_path, assistant_name="example"):
    
    with open(file_path, "r", encoding="utf-8") as json_file:
        try:
            article = json.load(json_file)
            idx = article['idx']
            title = article['title']
            abstract = article['abstract']
            journal = article['journal']
            publication_date = article['publication_date']
            authors = article['authors']
        except json.JSONDecodeError as e:
            print(f"Error reading {file_path}: {e}")
                        
                        
    assistant = pc.assistant.Assistant(
        assistant_name=assistant_name
    )
    
 
    #upload files
    response = assistant.upload_file(
        file_path=file_path,
        metadata={
            "idx": idx,
            "title": title,
            "abstract": abstract,
            "journal": journal,
            "publication_date" : publication_date,
            "authors": authors
            
            },
        timeout=None
    )
    print(f"Upload file {assistant_name} successfully.")

def input_query(query, assistant_name="example"):
    assistant = pc.assistant.Assistant(
        assistant_name=assistant_name
    )
    msg = Message(role="user", content=query)
    resp = assistant.chat(messages=[msg])
    return resp['message']['content']

def delete_assistant(assistant_name="example"):
    if check_assistant_name(assistant_name):
        pc.assistant.delete_assistant(
        assistant_name=assistant_name
    )
        print(f"Delete assistant_name {assistant_name} successfully.")
    else:
        print(f"{assistant_name} does not exist.")

def list_files(assistant_name="example"):
    assistant = pc.assistant.Assistant(
        assistant_name=assistant_name
    )
    files = assistant.list_files()
    # for file in files:
    #     print(file)
    return len(files)

def list_files_content(assistant_name="example"):
    assistant = pc.assistant.Assistant(
        assistant_name=assistant_name
    )
    files = assistant.list_files()
    for file in files:
        print(file)
    
        
def check_assistant_name(assistant_name="example"):
    """
    Checks if the assistant exists in Pinecone.
    """
    try:
        assistant = pc.assistant.Assistant(
            assistant_name=assistant_name
        )
        print(f"Assistant Name: {assistant.name}")
        return True
    except Exception as e:
        if "NOT_FOUND" in str(e):
            print(f"Assistant '{assistant_name}' does not exist.")
            return False
        else:
            raise e  # Re-raise other exceptions
    
def get_relative_paths_from_result():
    """
    Retrieves the relative paths of all files in the 'result' folder.
    """
    result_folder = "./medical_articles"
    if not os.path.exists(result_folder):
        print(f"The folder '{result_folder}' does not exist.")
        return []

    # Get all files in the result folder
    relative_paths = [
        os.path.join(result_folder, file)
        for file in os.listdir(result_folder)
        if os.path.isfile(os.path.join(result_folder, file))
    ]
    return relative_paths

def file_exists_in_pinecone(file_path, assistant_name="example"):
    """
    Checks if a file with the same title already exists in Pinecone.
    """
    assistant = pc.assistant.Assistant(
        assistant_name=assistant_name
    )
    files = assistant.list_files()
    
    # Extract the file name (or title) from the file path
    file_name = os.path.basename(file_path)
    # Check if the file name already exists in Pinecone
    for file in files:
        if file['name'] == file_name:
            return True
        
    return False 


def read_json_files(result_folder, max_files=10, assistant_name="example"):
    if not os.path.exists(result_folder):
            return (f"The folder '{result_folder}' does not exist.")
    else:
        # Iterate over all files in the result folder
        for file_name in os.listdir(result_folder):
            if list_files(assistant_name) < max_files:
                file_path = os.path.join(result_folder, file_name)
                if os.path.isfile(file_path):  # Ensure it's a file
                    # Check if the file exists in Pinecone
                    exists = file_exists_in_pinecone(file_path, assistant_name)
                    print(f"File '{file_name}' exists in Pinecone: {exists}")
                    if exists:
                        continue
                    else:
                        upload_files(file_path, assistant_name)
            else: 
                return (f"Pinecone allows uploading 10 files. The files are {list_files(assistant_name)}")  

def main(assistant_name):
    result_folder = "./medical_articles"
    if check_assistant_name(assistant_name):
        return read_json_files(result_folder)
    else:
        create_assistant(assistant_name)
        return read_json_files(result_folder)
        


      
        
        
def process_jsonl_line_by_line(file_path, assistant_name="amazonreview"):
    """
    Processes and uploads a JSONL file line by line to Pinecone.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                # Parse the line as a JSON object
                article = json.loads(line.strip())
                
                # Upload the JSON object to Pinecone
                upload_amazon_files(article, assistant_name)
                
         
             
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON on line {line_number}: {e}")
            except Exception as e:
                print(f"Error uploading JSON on line {line_number}: {e}")




def upload_amazon_files(article, assistant_name, max_retries=5):
    """
    Uploads a single article to Pinecone with retry logic.
    """
    assistant = pc.assistant.Assistant(
        assistant_name=assistant_name
    )
    
    # Convert the article to a JSON string
    article_content = json.dumps(article)

    # Write the JSON content to a temporary file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json", encoding="utf-8") as temp_file:
        temp_file.write(article_content)
        temp_file_path = temp_file.name

    # Upload the temporary file with retries
    for attempt in range(max_retries):
        try:
            response = assistant.upload_file(
                file_path=temp_file_path,  # Use 'file' to specify the file path
                metadata={
                    "rating": article.get('rating'),
                    "title": article.get('title'),
                    "text": article.get('text'),
                    "images": [],
                    "asin": article.get("asin"),
                    "parent_asin": article.get('parent_asin'),
                    "user_id": article.get('user_id'),
                    "timestamp": article.get('timestamp'),
                    "helpful_vote": article.get('helpful_vote'),
                    "verified_purchase": article.get('verified_purchase')
                },
                timeout=None
            )
            print(f"Uploaded article '{article.get('title')}' successfully.")
            break  # Exit the retry loop on success
        except Exception as e:
            print(f"Error uploading article '{article.get('title')}' (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"Failed to upload article '{article.get('title')}' after {max_retries} attempts.")
        finally:
            # Clean up the temporary file
            os.remove(temp_file_path)
        
# if __name__ == "__main__":
    
#     assistant_name = "amazonreview"
    # process_jsonl_line_by_line("./amazon_review/All_Beauty.jsonl", assistant_name)   
    # check_assistant_name(assistant_name)
    # list_files_content(assistant_name)
    # query = "how many files can I load in a free model?"
    # file_path = "./medical_articles/A Machine Learning Model for Predicting Diabetic Nephropathy Based on TG_Cys-C Ratio and Five Clinical Indicators.json"
    # result_folder = "./amazon_review"
    # create_assistant(assistant_name)
    # upload_files(file_path, "title", "author", "abstract", "journal", assistant_name)
    # ans = input_query(query, assistant_name)
    # print(ans)
    # print(list_files(assistant_name))
    # delete_assistant(assistant_name)

    # relative_paths = get_relative_paths_from_result()
    # print("Files in the 'result' folder:")
    # for file_path in relative_paths:
    #     upload_files(file_path, "title", "author", "abstract", "journal", assistant_name)
    #ans = input_query(query, assistant_name)
    #print(ans)
    
    # Ensure the result folder exists
    # max_files = 10
    # if check_assistant_name(assistant_name):
    #     read_json_files(result_folder, max_files)
    # else:
    #     create_assistant(assistant_name)
    #     read_json_files(result_folder, max_files)

    # print(list_files(assistant_name))



    