from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import shutil
from gemini import main
from trailer import generate_highlights

app = Flask(__name__)

# Set the upload folder
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/highlights', methods=['POST'])
def load_route():
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
        
        # Check video extension
        video_extensions = ('.mp4', '.avi', '.wmv', '.mov')
        try:
            if filename.lower().endswith(video_extensions):
                main(file_path)
                generate_highlights(file_path)
                return jsonify({'message': f'Generated Highlights Successfully.'}), 200
            else:
                return jsonify({'error': f'Unsupported file type for file {filename}'}), 400

        except Exception as e:
            import traceback
            print(traceback.format_exc())  # Print detailed error for debugging
            return jsonify({'error': str(e)}), 500

        finally:
            # Clean up the entire upload directory
            shutil.rmtree(upload_dir, ignore_errors=True)
        

if __name__ == '__main__':
    app.run(debug=True, port=5002)

