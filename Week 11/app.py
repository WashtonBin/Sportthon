import shutil
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from mcp_demo import sql_prompt
import os
import asyncio


app = Flask(__name__)

# Set the upload folder
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

"""
        For pubmed.py and pinecone_assistant.py
    
"""       
@app.route('/sqlite', methods=['POST'])
def sqlite_prompt_route():
    data = request.form.to_dict()
    try:
        if not data:
            return jsonify({
                "error": "Missing 'query' in request body",
                "example": {"query": "write a sql query"},
                
            }), 400
            
        query = data['query']

        result = sql_prompt(query)
        
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
        
        
@app.route('/create_table', methods=['POST'])
def create_table_route():
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
    
    try:
        if not data:
            return jsonify({
                "error": "Missing 'query' in request body",
                "example": {"query": "write a sql query"},
                
            }), 400
            
        query = data['query']

        result = sql_prompt(query)
        
        # Return the save files
        return jsonify({
            "query": query,
            "response": result,
            "status": "success"
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())  # Print detailed error for debugging
        return jsonify({'error': str(e)}), 500

    finally:
        # Clean up the entire upload directory
        shutil.rmtree(upload_dir, ignore_errors=True)



if __name__ == '__main__':
    app.run(debug=True, port=5002)

