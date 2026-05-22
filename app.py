from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from resume_analyzer import ResumeAnalyzer

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = '/tmp' if os.environ.get('VERCEL') else 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize analyzer
analyzer = ResumeAnalyzer()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    has_api_key = bool(
        os.environ.get("GEMINI_API_KEY") or 
        os.environ.get("GROK_API_KEY") or 
        os.environ.get("OPENAI_API_KEY") or
        analyzer.api_key
    )
    return render_template('index.html', api_configured=has_api_key)

@app.route('/api/analyze', methods=['POST'])
def analyze_resume():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload PDF, DOC, DOCX, or TXT'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Get job description if provided
            job_description = request.form.get('job_description')
            
            # Analyze resume
            analysis = analyzer.analyze(filepath, job_description)
            
            # Clean up uploaded file
            os.remove(filepath)
            
            return jsonify(analysis)
        except Exception as e:
            # Clean up on error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-text', methods=['POST'])
def analyze_text():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        job_description = data.get('job_description')
        
        if not text.strip():
            return jsonify({'error': 'Empty text provided'}), 400
        
        # Analyze text directly
        analysis = analyzer.analyze_text(text, job_description)
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
