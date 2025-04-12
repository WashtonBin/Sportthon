import json
def read_from_json(path):
    try:
        with open(path, 'r') as file:
            content = json.load(file)
            return content
    except FileNotFoundError:
        print("The file does not exist.")
    except KeyError:
        print(f"The field  does not exist in the JSON file.")
    except json.JSONDecodeError:
        print("Error decoding JSON.")
    except Exception as e:
        print(f"An error occurred: {e}") 
        
      
def store_response_in_json(response_text, filename):
    """Stores the Gemini API response in a JSON file."""
    if response_text:
        try:
            # Attempt to parse the response as JSON
            data = json.loads(response_text)
        except json.JSONDecodeError:
            # If it's not valid JSON, store it as a string
            data = {"response": response_text}

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Response stored in {filename}")
    else:
        print("No response to store.")
        
        
    

