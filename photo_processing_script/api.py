from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from main import process_image

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/process-image', methods=['POST'])
def handle_image_processing():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400
    
    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path)

        # Process the image
        watermark_path = 'watermark_khalas.png'
        output_path = app.config['UPLOAD_FOLDER']

        processed_image_name = process_image(root_path=None, watermark_path=watermark_path, output_path=output_path, image_path=image_path)
        
        # Return the processed image
        return send_file(processed_image_name, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)