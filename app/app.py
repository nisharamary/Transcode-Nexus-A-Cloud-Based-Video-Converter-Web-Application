from flask import Flask, request, render_template, send_from_directory
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Absolute paths to prevent 404 issues
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
CONVERTED_FOLDER = os.path.join(BASE_DIR, 'converted')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'webm'}

# App configurations
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# Ensure required folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        file = request.files.get('video')
        output_format = request.form.get('format')

        if file and allowed_file(file.filename) and output_format:
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)

            base = os.path.splitext(filename)[0]
            output_filename = f"{base}.{output_format}"
            output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)

            # Convert using FFmpeg
            subprocess.run(['ffmpeg', '-y', '-i', input_path, output_path])

            return render_template('success.html', output_filename=output_filename)
        else:
            return 'Invalid file or format.', 400

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['CONVERTED_FOLDER'], filename, as_attachment=True)

# Optional: debug file listing
@app.route('/debug-files')
def debug_files():
    files = os.listdir(app.config['CONVERTED_FOLDER'])
    return '<br>'.join(files)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
