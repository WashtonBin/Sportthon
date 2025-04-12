import shutil
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import pubmed
import pinecone_assistant
import pinecone_chatbot as pc
import os
import searchbox_suggestions as ss

app = Flask(__name__)

# Set the upload folder
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

"""
        For pubmed.py and pinecone_assistant.py
    
"""       
@app.route('/pubmed', methods=['POST'])
def pubmed_route():
    data = request.form.to_dict()
    try:
        if not data:
            return jsonify({
                "error": "Missing 'category' in request body",
                "example": {"category": "What is the main medical topic would you like to fetch from https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"},
                
            }), 400
            
        category = data['category']

        article_number = pubmed.main(category)
        print(article_number)
        # Return the save files
        return jsonify({
            "query": category,
            "response": article_number,
            "status": "success"
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "traceback": error_trace,
            "status": "error"
        }), 500
        
        
@app.route('/generate_pinecone', methods=['POST'])
def generate_pinecone():
    data = request.form.to_dict()
    try:
        if not data:
            return jsonify({
                "error": "Missing 'assistant_name' in request body",
                "example": {"assistant_name": "Building your own assistant_name"},
                
            }), 400
            
        assistant_name = data['assistant_name']

        result = pinecone_assistant.main(assistant_name)
  
        # Return the save files
        return jsonify({
            "assistant_name": assistant_name,
            "response": result,
            "status": "success"
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "traceback": error_trace,
            "status": "error"
        }), 500
        
@app.route('/ask_pinecone', methods=['POST'])
def ask_pinecone_route():
    data = request.form.to_dict()
    try:
        if not data:
            return jsonify({
                "error": "Missing 'query' in request body",
                "example": {"query": "Asking a question related to the topic"},
                
            }), 400
            
        query = data['query']

        result = pinecone_assistant.input_query(query)
        print(result)
        # Return the save files
        return jsonify({
            "query": query,
            "response": result,
            "status": "success"
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "traceback": error_trace,
            "status": "error"
        }), 500
        



    """
        For pinecone_chatbot.py
    
    """


@app.route('/load_json', methods=['POST'])
def load_json_route():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    files = request.files.getlist('file')
    if not files:
        return jsonify({'error': 'No selected files'}), 400

    for file in files:
        if file.filename == '':
            return jsonify({'error': 'One of the selected files has no filename'}), 400

        filename = secure_filename(file.filename)
        # Create a unique directory for this upload
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'])
        os.makedirs(upload_dir, exist_ok=True)
    
        file_path = os.path.join(upload_dir, filename)
        print(file_path)
        file.save(file_path)
        
        
    data = request.form.to_dict()
    
    if not data:
        return jsonify({
            "error": "Missing 'index_name' in request body",
            "example": {"query": "Asking a question related to the topic"},
            
        }), 400
            
    index_name = data['index_name']
    
    # Check video extension
    video_extensions = ('.jsonl')
    try:
        if filename.lower().endswith(video_extensions):
            result = pc.load_data(file_path, index_name)
            print(result)
            return jsonify({'message': result}), 200
        else:
            return jsonify({'error': f'Unsupported file type for file {filename}'}), 400

    except Exception as e:
        import traceback
        print(traceback.format_exc())  # Print detailed error for debugging
        return jsonify({'error': str(e)}), 500

    finally:
        # Clean up the entire upload directory
        shutil.rmtree(upload_dir, ignore_errors=True)
        
        
@app.route('/pinecone_chatbot', methods=['POST'])
def pinecone_chatbot_route():
    data = request.form.to_dict()
    try:
        if not data:
            return jsonify({
                "error": "Missing 'query' or 'index_name' in request body",
                "example": {"query": "Asking a question related to the topic"},
                
            }), 400
            
        query = data['query']
        index_name = data['index_name']
        result = pc.ask_query(query, index_name)
        print(result)
        # Return the save files
        return jsonify({
            "query": query,
            "answer": result['answer'],
            "status": "success"
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "traceback": error_trace,
            "status": "error"
        }), 500


    """
    
    for searchbox_suggestions.py
    """
    
@app.route('/searchbox', methods=['POST'])
def searchbox_route():
    data = request.form.to_dict()
    try:
        if not data:
            return jsonify({
                "error": "Missing 'query' in request body",
                "example": {"query": "enter a query to search"},
                
            }), 400
            
        query = data['query']

        result = ss.suggestions(query)
  
        # Return the save files
        return jsonify({
            "query": query,
            "response": result,
            "status": "success"
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "traceback": error_trace,
            "status": "error"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)

