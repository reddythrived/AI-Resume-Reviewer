# AI Resume Analyzer & ATS Copilot

A sophisticated, high-performance resume diagnostic platform that leverages **Generative AI (LLMs)** and **Natural Language Processing** to transform standard resumes into career-winning documents.

## 🚀 Advanced Features

- **🤖 Context-Aware LLM Analysis**: Deep semantic evaluation using Large Language Models to analyze the "Impact" of your bullet points.
- **🎯 ATS Simulation Engine**: Paste a target Job Description to simulate how real-world Applicant Tracking Systems will rank your profile.
- **⚡ Bullet Point Optimizer**: AI-driven suggestions to rewrite weak duties into high-impact, metric-driven achievements using the STAR/XYZ formula.
- **📄 Multi-format Parsing**: Advanced extraction from PDF, DOCX, and TXT using PyPDF2 and python-docx.
- **📊 Interactive Visualizations**: Dynamic Chart.js dashboard for ATS Compatibility, Readability, and Section Completeness scores.
- **💡 Strategic Career Advice**: Personalized top-3 strategic recommendations to land specific roles based on current market trends.
- **🎨 Premium Midnight UI**: Glassmorphic, responsive interface with high-end animations and "Midnight" aesthetic.

## 🛠 Technology Stack

- **AI/LLM Core**: x.ai (Grok) / Google Gemini API integration for semantic reasoning.
- **Backend**: Flask (Python) with asynchronous thread management for non-blocking API calls.
- **NLP**: spaCy (Named Entity Recognition), NLTK (Tokenization), TextStat (Readability Scoring).
- **Frontend**: Vanilla JavaScript with **Chart.js** for data visualization.
- **Styling**: Advanced CSS3 with glassmorphism, radial gradients, and fluid typography.

## 📦 Installation & Setup

1. **Clone the repository**
2. **Configure Environment**:
   Create a `.env` file in the root:
   ```env
   GROK_API_KEY=your_api_key_here
   FLASK_DEBUG=true
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Download NLP Models**:
   ```bash
   python -m spacy download en_core_web_sm
   ```
5. **Launch**:
   ```bash
   python app.py
   ```

## 📈 Analysis Logic

### 1. The ATS Similarity Engine
Uses semantic reasoning to match candidate skills and experience against a provided Job Description, identifying critical missing keywords that would otherwise trigger an ATS rejection.

### 2. Impact-Based Scoring
Unlike traditional keyword counters, this system uses LLMs to evaluate the *quality* of content, rewarding achievements that include quantifiable metrics and strong action verbs.

### 3. Readability & Logistics
Evaluates the Flesch-Kincaid ease of reading and checks for common resume formatting issues that confuse automated scanners.

## ✅ Completed Enhancements
- [x] ATS (Applicant Tracking System) compatibility scoring
- [x] Context-aware bullet point rewrites
- [x] Resume comparison with job descriptions
- [x] Advanced data visualization with Chart.js
- [x] Generative AI integration

---
**Built for high-impact career placement | Powered by Advanced AI**
