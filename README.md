# AI Resume Analyzer

A powerful, AI-driven resume analysis tool built with Flask and NLP technologies. Get instant insights about your resume's quality, completeness, and areas for improvement.

## Features

- **📄 Multi-format Support**: Upload PDF, DOC, DOCX, or TXT files
- **🤖 AI-Powered Analysis**: Advanced NLP processing using spaCy and NLTK
- **📊 Comprehensive Scoring**: Get detailed scores on completeness, skills, experience, education, readability, and length
- **💡 Smart Suggestions**: Receive actionable improvement recommendations
- **🎨 Modern UI**: Beautiful, responsive dark-themed interface
- **⚡ Real-time Analysis**: Fast and efficient processing

## Technology Stack

- **Backend**: Flask (Python)
- **NLP**: spaCy, NLTK, TextStat
- **File Processing**: PyPDF2, python-docx
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Modern CSS with gradients and animations

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup Steps

1. **Clone or download this repository**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download spaCy language model**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Project Structure

```
AI Resume reviewer/
│
├── app.py                 # Flask application and API endpoints
├── resume_analyzer.py     # Core NLP analysis logic
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
│
├── templates/
│   └── index.html        # Main frontend template
│
├── static/
│   ├── css/
│   │   └── style.css    # Styling and animations
│   └── js/
│       └── main.js      # Frontend JavaScript logic
│
└── uploads/              # Temporary file storage (created automatically)
```

## Usage

1. **Upload a Resume**:
   - Click "Choose file" to browse for your resume
   - Or drag and drop your resume file
   - Supported formats: PDF, DOC, DOCX, TXT

2. **Or Paste Text**:
   - Paste your resume text directly into the text area

3. **Analyze**:
   - Click "Analyze Resume" button
   - Wait for the AI to process your resume

4. **Review Results**:
   - View overall rating and score
   - Check detailed statistics
   - Review score breakdown
   - See detected skills
   - Read improvement suggestions

5. **Take Action**:
   - Use suggestions to improve your resume
   - Download the analysis report
   - Analyze another resume

## API Endpoints

### POST `/api/analyze`
Upload a resume file for analysis.

**Request**: Multipart form data with `file` field
**Response**: JSON with analysis results

### POST `/api/analyze-text`
Analyze resume text directly.

**Request**: JSON with `text` field
**Response**: JSON with analysis results

## Analysis Features

### Statistics
- Word count
- Character count
- Sentence count
- Readability score (Flesch Reading Ease)

### Sections Detection
- Contact Information
- Summary/Objective
- Work Experience
- Education
- Skills
- Projects
- Certifications

### Skills Extraction
Automatically detects technical skills and competencies mentioned in your resume.

### Scoring System
- **Completeness**: Based on sections present
- **Skills**: Number and relevance of skills
- **Experience**: Work experience details
- **Education**: Educational background
- **Readability**: Text clarity and complexity
- **Length**: Optimal resume length (400-800 words)

### Suggestions
Prioritized recommendations for improving your resume:
- High priority: Critical improvements
- Medium priority: Important enhancements

## Customization

### Adding More Skills Keywords
Edit `resume_analyzer.py` and add keywords to the `skills_keywords` list.

### Adjusting Scoring Weights
Modify the `weights` dictionary in the `_calculate_overall_rating` method.

### Styling
Customize colors and styles in `static/css/style.css` using CSS variables.

## 🌐 Deployment - Make It Global

Your app is already configured for cloud deployment! Here's how to deploy it:

### Option 1: Railway (Recommended - Free & Easy)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy AI Resume Analyzer"
   git push origin main
   ```

2. **Deploy on Railway**:
   - Go to https://railway.app
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Python and deploys
   - Get your public URL: `https://your-app.up.railway.app`

3. **Share your global link!** 🎉

### Option 2: Render

1. Go to https://render.com
2. Sign up with GitHub
3. New Web Service → Connect GitHub repo
4. Build Command: `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
5. Start Command: `python app.py`
6. Deploy and get URL: `https://your-app.onrender.com`

### Option 3: PythonAnywhere

1. Go to https://www.pythonanywhere.com
2. Upload files or clone from GitHub
3. Create Web App → Flask
4. Configure and deploy
5. Get URL: `https://yourname.pythonanywhere.com`

**Your app uses `PORT` environment variable automatically - no code changes needed!**

## Troubleshooting

### spaCy Model Not Found
If you see a warning about the spaCy model:
```bash
python -m spacy download en_core_web_sm
```

### File Upload Issues
- Ensure file size is under 5MB
- Check file format is supported (PDF, DOC, DOCX, TXT)
- Verify file is not corrupted

### Port Already in Use
The app automatically uses the PORT environment variable. For local testing:
```python
# Already configured in app.py - uses PORT env var or defaults to 5000
```

## Future Enhancements

- [ ] ATS (Applicant Tracking System) compatibility scoring
- [ ] Industry-specific analysis
- [ ] Resume comparison with job descriptions
- [ ] Export to PDF/Word format
- [ ] Multi-language support
- [ ] Advanced entity recognition
- [ ] Resume templates and builder

## License

This project is open source and available for educational and commercial use.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or suggestions, please open an issue on the repository.

---

**Built with ❤️ using Flask, NLP, and modern web technologies**
