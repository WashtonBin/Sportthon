import google.generativeai as genai
import base64
import os
import json
from dotenv import load_dotenv


load_dotenv()

gemini_key = os.getenv('GEMINI_API_KEY')

def generate(video_path):
    genai.configure(api_key=gemini_key)

    model = genai.GenerativeModel('gemini-2.0-flash')

    # Path to your local video file
    local_video_path = video_path

    # Encode the video file to base64
    with open(local_video_path, "rb") as video_file:
        video_data = video_file.read()
        video_base64 = base64.b64encode(video_data).decode("utf-8")

    # Prepare the content
    content = [
        {"mime_type": "video/mp4", "data": video_base64},
        """Highlight the video content by grouping the video content into chapters and providing a summary for Highlight chapter. Please capture the most important key scenes and highlights. If you are not sure about any info, please do not make it up. Return the 
        result in the JSON format with keys as follows : "start-time", "end-time", "chapterSummary" """
    ]

    try:
        response = model.generate_content(content)
        response_text = response.text  # Get the text from the response
        return response_text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

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
        
        
def pick_most_important_highlights(json_file="response.json"):
    """
    Reads a JSON file, extracts highlights, and uses Gemini to pick the most important ones.
    """
    try:
        with open(json_file, "r") as f:
            data = json.load(f)
            # Extract the JSON string from the response
            response_string = data['response']
            # Remove ```json and ``` from the string
            response_string = response_string.replace('```json', '').replace('```', '')
            highlights = json.loads(response_string)
    except FileNotFoundError:
        return "Error: response.json not found."
    except json.JSONDecodeError:
        return "Error: Could not decode JSON from response.json."
    except KeyError:
        return "Error: 'response' key not found in response.json."

    # Initialize Gemini
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    # Prepare the prompt for Gemini
    prompt = f"""
    You are an expert video editor. Given the following video highlights, identify the most important highlights that capture the essence of the video.
    Return the result in the JSON format with keys as follows : "start-time", "end-time", "chapterSummary".
    Here are the video highlights:
    {highlights}
    """

    try:
        response = model.generate_content(prompt)
        # Extract the JSON string from the response
        response_string = response.text
        # Remove ```json and ``` from the string
        response_string = response_string.replace('```json', '').replace('```', '')
        # Parse the JSON string
        important_highlights = json.loads(response_string)
        return important_highlights
    except Exception as e:
        return f"Error: Could not generate highlights using Gemini. {e}"

def main(video_path):
    # Generate the content and store the response
    response_text = generate(video_path)
    print(response_text)
    store_response_in_json(response_text, "response.json")
    highlights = pick_most_important_highlights("response.json")
    store_response_in_json(json.dumps(highlights), "highlights.json")
