import os
from main import process_image

from flask import Flask, request, jsonify, send_file, after_this_request, make_response
from flask_cors import CORS, cross_origin

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from tempfile import mkdtemp
from zipfile import ZipFile
import shutil

UPLOAD_FOLDER = 'uploads'
WATERMARK_PATH = 'watermark_khalas.png'
PROCESSED_IMAGES_ARCHIVE = 'processed_images.zip'

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type, Content-Disposition'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['WATERMARK_PATH'] = WATERMARK_PATH
app.config['PROCESSED_IMAGES_ARCHIVE'] = PROCESSED_IMAGES_ARCHIVE

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def cleanup_temp_files(temp_dir=None):
    """Decorator function for cleaning up files and directories after a request"""
    @after_this_request
    def remove_files_and_dirs(response):
        if temp_dir:
            # Remove the temporary directory used for zipping files
            try:
                shutil.rmtree(temp_dir)
            except Exception as error:
                app.logger.error(f"Error removing temporary directory {temp_dir}: {error}")

        # Clear contents of the upload directory
        upload_folder = app.config['UPLOAD_FOLDER']
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as error:
                app.logger.error(f"Failed to delete {file_path}. Reason: {error}")

        return response

    return remove_files_and_dirs

def process_file(file: FileStorage) -> str:
    """Utility function for temporarily storing a file, then processing it using the main script"""
    filename = secure_filename(file.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(image_path)
    
    watermark_path = app.config['WATERMARK_PATH']
    output_path = app.config['UPLOAD_FOLDER']

    # Process the image
    processed_image_path = process_image(root_path=None, watermark_path=watermark_path, output_path=output_path, image_path=image_path)
    
    return processed_image_path

@app.route('/process-images', methods=['POST'])
@cross_origin()
def handle_image_processing():
    """
    Endpoint for processing single or multiple images.\n
    In case one single image is uploaded, one single parsed image is returned as binary data,\n
    otherwise, a zip file containing all the processed images is returned.
    """
    if 'images' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400
    
    files = request.files.getlist('images')

    if not files or any(file.filename == '' for file in files):
        return jsonify({'error': 'No selected files'}), 400


    # Single file processing
    if len(files) == 1:
        file = files[0]
        try:
          processed_image_path = process_file(file)
        except Exception as error:
            return jsonify({'error': f'Error processing image: {error}'}), 400

        cleanup_temp_files()
        
        response = make_response(send_file(processed_image_path, mimetype='image/jpeg', as_attachment=True, download_name=os.path.basename(processed_image_path)))
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return response

    # Multiple file processing
    else:
        temp_dir = mkdtemp()
        zip_path = os.path.join(temp_dir, app.config['PROCESSED_IMAGES_ARCHIVE'])

        with ZipFile(zip_path, 'w') as zipf:
            for file in files:
                try:
                  processed_image_path = process_file(file)
                except Exception as error:
                    return jsonify({'error': f'Error processing image: {error}'}), 400

                zipf.write(processed_image_path, os.path.basename(processed_image_path))

        cleanup_temp_files(temp_dir=temp_dir)
        response = make_response(send_file(zip_path, mimetype='application/zip', as_attachment=True, download_name=app.config['PROCESSED_IMAGES_ARCHIVE']))
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return response


if __name__ == '__main__':
    app.run(debug=True)