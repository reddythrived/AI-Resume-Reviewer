import re
import os
import PyPDF2
from docx import Document
import spacy
import nltk
from textstat import flesch_reading_ease, syllable_count
from collections import Counter
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

class ResumeAnalyzer:
    def __init__(self):
        # Try to load spaCy model, auto-download if not available
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model 'en_core_web_sm' not found. Attempting download...")
            try:
                from spacy.cli import download
                download("en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
            except Exception as e:
                print(f"Warning: Could not download spaCy model: {e}. Using basic NLP fallback.")
                self.nlp = None
        
        self.stop_words = set(stopwords.words('english'))
        self.grok_api_key = os.environ.get("GROK_API_KEY")
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.api_key = self.grok_api_key or self.gemini_api_key or self.openai_api_key
        
        # Keywords for different sections
        self.skills_keywords = [
            'python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker',
            'kubernetes', 'git', 'machine learning', 'ai', 'data science', 'tensorflow',
            'pytorch', 'flask', 'django', 'mongodb', 'postgresql', 'linux', 'agile',
            'scrum', 'ci/cd', 'rest api', 'graphql', 'microservices', 'cloud computing'
        ]
        
        self.education_keywords = [
            'bachelor', 'master', 'phd', 'degree', 'university', 'college',
            'education', 'graduated', 'gpa', 'cgpa', 'bachelor\'s', 'master\'s'
        ]
        
        self.experience_keywords = [
            'experience', 'worked', 'years', 'responsible', 'developed', 'managed',
            'led', 'implemented', 'created', 'designed', 'achieved', 'improved'
        ]

    def refresh_keys(self):
        """Refresh API keys from environment variables dynamically."""
        self.grok_api_key = os.environ.get("GROK_API_KEY")
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.api_key = self.grok_api_key or self.gemini_api_key or self.openai_api_key

    def extract_text_from_file(self, filepath):
        """Extract text from PDF, DOCX, or TXT file"""
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.pdf':
            return self._extract_from_pdf(filepath)
        elif ext in ['.doc', '.docx']:
            return self._extract_from_docx(filepath)
        elif ext == '.txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def _extract_from_pdf(self, filepath):
        """Extract text from PDF file"""
        text = ""
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _extract_from_docx(self, filepath):
        """Extract text from DOCX file"""
        doc = Document(filepath)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def analyze(self, filepath, job_description=None):
        """Analyze resume from file"""
        text = self.extract_text_from_file(filepath)
        return self.analyze_text(text, job_description)

    def analyze_text(self, text, job_description=None):
        """Comprehensive resume analysis"""
        self.refresh_keys()
        if not text or not text.strip():
            return {'error': 'Empty text provided'}
        
        text = text.strip()
        
        # Basic statistics
        word_count = len(word_tokenize(text))
        char_count = len(text)
        sentence_count = len(sent_tokenize(text))
        
        # Extract sections
        sections = self._extract_sections(text)
        
        # Extract entities
        entities = self._extract_entities(text)
        
        # Extract skills
        skills = self._extract_skills(text)
        
        # Extract education
        education = self._extract_education(text)
        
        # Extract experience
        experience = self._extract_experience(text)
        
        # Calculate scores
        scores = self._calculate_scores(text, sections, skills, education, experience)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(text, sections, skills, education, experience, scores)
        
        result = {
            'statistics': {
                'word_count': word_count,
                'char_count': char_count,
                'sentence_count': sentence_count,
                'readability_score': flesch_reading_ease(text)
            },
            'sections': sections,
            'entities': entities,
            'skills': skills,
            'education': education,
            'experience': experience,
            'scores': scores,
            'suggestions': suggestions,
            'overall_rating': self._calculate_overall_rating(scores)
        }

        # Select and run the appropriate LLM analyzer, or fallback to heuristics
        ai_analysis = None
        if self.gemini_api_key:
            ai_analysis = self._analyze_with_gemini(text, job_description)
        elif self.grok_api_key:
            ai_analysis = self._analyze_with_llm(text, job_description)
        elif self.openai_api_key:
            ai_analysis = self._analyze_with_openai(text, job_description)
        
        # Fallback to local heuristic analyzer if cloud API fails or no API keys are present
        if not ai_analysis or 'error' in ai_analysis:
            if ai_analysis and 'error' in ai_analysis:
                print(f"Cloud LLM analysis failed: {ai_analysis['error']}. Falling back to local analyzer.")
            ai_analysis = self._analyze_with_fallback(text, job_description)
            
        result['ai_analysis'] = ai_analysis
        return result

    def _analyze_with_llm(self, resume_text, job_description=None):
        """Perform deep semantic analysis using an LLM."""
        if not self.api_key:
            return None

        jd_prompt = ""
        score_instruction = "The 'score' under 'ats_compatibility' must evaluate the overall strength and professional quality of the resume on a scale of 0-100 (rating layout, metrics, clarity, and content)."
        if job_description:
            jd_prompt = f"\nTARGET JOB DESCRIPTION:\n{job_description}\n"
            score_instruction = "The 'score' under 'ats_compatibility' must evaluate the ATS compatibility/match score (0-100) between the resume and the target job description (how well the skills, experience, and content align with the job requirements)."

        prompt = f"""
        You are an expert technical recruiter and ATS (Applicant Tracking System) specialist.
        Analyze the following resume and provide a high-level, professional critique.
        {jd_prompt}
        RESUME CONTENT:
        {resume_text}

        INSTRUCTIONS:
        {score_instruction}

        Return ONLY valid JSON with this structure:
        {{
            "summary": "Professional executive summary of the candidate's profile.",
            "ats_compatibility": {{
                "score": 0-100,
                "missing_keywords": ["keyword1", "keyword2"],
                "formatting_issues": ["issue1"]
            }},
            "impact_analysis": [
                {{
                    "original": "original bullet point",
                    "critique": "why it's weak",
                    "optimized": "suggested high-impact version using action verbs and metrics"
                }}
            ],
            "skills_categorization": {{
                "Frontend": [],
                "Backend": [],
                "DevOps/Cloud": [],
                "Tools/Others": []
            }},
            "strategic_advice": "Top 3 strategic things this person should do to land this role."
        }}
        """

        try:
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-beta",
                    "messages": [
                        {"role": "system", "content": "You are a clinical career AI. Respond only in valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.4
                },
                timeout=30
            )
            data = response.json()
            return json.loads(self._clean_json_string(data["choices"][0]["message"]["content"]))
        except Exception as e:
            print(f"LLM Analysis Error: {str(e)}")
            return {"error": "LLM Analysis failed"}

    def _clean_json_string(self, text):
        """Strip markdown code blocks from a JSON response if present."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def _analyze_with_gemini(self, resume_text, job_description=None):
        """Perform deep semantic analysis using Google Gemini API."""
        if not self.gemini_api_key:
            return None

        jd_prompt = ""
        score_instruction = "The 'score' under 'ats_compatibility' must evaluate the overall strength and professional quality of the resume on a scale of 0-100 (rating layout, metrics, clarity, and content)."
        if job_description:
            jd_prompt = f"\nTARGET JOB DESCRIPTION:\n{job_description}\n"
            score_instruction = "The 'score' under 'ats_compatibility' must evaluate the ATS compatibility/match score (0-100) between the resume and the target job description (how well the skills, experience, and content align with the job requirements)."

        prompt = f"""
        You are an expert technical recruiter and ATS (Applicant Tracking System) specialist.
        Analyze the following resume and provide a high-level, professional critique.
        {jd_prompt}
        RESUME CONTENT:
        {resume_text}

        INSTRUCTIONS:
        {score_instruction}

        Return ONLY valid JSON with this structure:
        {{
            "summary": "Professional executive summary of the candidate's profile.",
            "ats_compatibility": {{
                "score": 0-100,
                "missing_keywords": ["keyword1", "keyword2"],
                "formatting_issues": ["issue1"]
            }},
            "impact_analysis": [
                {{
                    "original": "original bullet point",
                    "critique": "why it's weak",
                    "optimized": "suggested high-impact version using action verbs and metrics"
                }}
            ],
            "skills_categorization": {{
                "Frontend": [],
                "Backend": [],
                "DevOps/Cloud": [],
                "Tools/Others": []
            }},
            "strategic_advice": "Top 3 strategic things this person should do to land this role."
        }}
        """

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            res_json = response.json()
            content_text = res_json['candidates'][0]['content']['parts'][0]['text']
            return json.loads(self._clean_json_string(content_text))
        except Exception as e:
            print(f"Gemini Analysis Error: {str(e)}")
            return {"error": f"Gemini Analysis failed: {str(e)}"}

    def _analyze_with_openai(self, resume_text, job_description=None):
        """Perform deep semantic analysis using OpenAI API."""
        if not self.openai_api_key:
            return None

        jd_prompt = ""
        score_instruction = "The 'score' under 'ats_compatibility' must evaluate the overall strength and professional quality of the resume on a scale of 0-100 (rating layout, metrics, clarity, and content)."
        if job_description:
            jd_prompt = f"\nTARGET JOB DESCRIPTION:\n{job_description}\n"
            score_instruction = "The 'score' under 'ats_compatibility' must evaluate the ATS compatibility/match score (0-100) between the resume and the target job description (how well the skills, experience, and content align with the job requirements)."

        prompt = f"""
        You are an expert technical recruiter and ATS (Applicant Tracking System) specialist.
        Analyze the following resume and provide a high-level, professional critique.
        {jd_prompt}
        RESUME CONTENT:
        {resume_text}

        INSTRUCTIONS:
        {score_instruction}

        Return ONLY valid JSON with this structure:
        {{
            "summary": "Professional executive summary of the candidate's profile.",
            "ats_compatibility": {{
                "score": 0-100,
                "missing_keywords": ["keyword1", "keyword2"],
                "formatting_issues": ["issue1"]
            }},
            "impact_analysis": [
                {{
                    "original": "original bullet point",
                    "critique": "why it's weak",
                    "optimized": "suggested high-impact version using action verbs and metrics"
                }}
            ],
            "skills_categorization": {{
                "Frontend": [],
                "Backend": [],
                "DevOps/Cloud": [],
                "Tools/Others": []
            }},
            "strategic_advice": "Top 3 strategic things this person should do to land this role."
        }}
        """

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are a clinical career AI. Respond only in valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.4
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(self._clean_json_string(content))
        except Exception as e:
            print(f"OpenAI Analysis Error: {str(e)}")
            return {"error": f"OpenAI Analysis failed: {str(e)}"}

    def _analyze_with_fallback(self, text, job_description=None):
        """Fallback analysis when no LLM API key is present."""
        skills = self._extract_skills(text)
        
        frontend_keywords = ['react', 'angular', 'vue', 'html', 'css', 'javascript', 'typescript', 'frontend', 'jquery', 'bootstrap', 'tailwind']
        backend_keywords = ['python', 'java', 'node', 'express', 'django', 'flask', 'sql', 'mongodb', 'postgresql', 'backend', 'c#', 'c++', 'ruby', 'php', 'golang']
        devops_keywords = ['aws', 'docker', 'kubernetes', 'ci/cd', 'git', 'linux', 'azure', 'gcp', 'jenkins', 'terraform', 'ansible']
        
        skills_cat = {
            "Frontend": [],
            "Backend": [],
            "DevOps/Cloud": [],
            "Tools/Others": []
        }
        
        for s in skills:
            s_lower = s.lower()
            if any(k in s_lower for k in frontend_keywords):
                skills_cat["Frontend"].append(s)
            elif any(k in s_lower for k in backend_keywords):
                skills_cat["Backend"].append(s)
            elif any(k in s_lower for k in devops_keywords):
                skills_cat["DevOps/Cloud"].append(s)
            else:
                skills_cat["Tools/Others"].append(s)
                
        # Find missing keywords if Job Description is provided
        missing_kw = []
        if job_description:
            jd_lower = job_description.lower()
            for kw in self.skills_keywords:
                if kw in jd_lower and kw.title() not in skills:
                    missing_kw.append(kw.title())
            if not missing_kw:
                missing_kw = ["System Design", "Scalability", "Agile Methodologies"]
        else:
            missing_kw = ["Quantifiable Metrics", "Action Verbs", "Profile Summary"]
            
        # Basic formatting check
        formatting_issues = []
        sections = self._extract_sections(text)
        if not sections.get('summary'):
            formatting_issues.append("Missing professional summary section at the top of the resume.")
        if not sections.get('contact'):
            formatting_issues.append("Contact details section not clearly identified. Ensure email and phone are easy to parse.")
        
        word_count = len(text.split())
        if word_count > 1000:
            formatting_issues.append("Resume exceeds 1000 words. Try to keep it concise and under 2 pages.")
        elif word_count < 300:
            formatting_issues.append("Resume is under 300 words. Add more details about achievements and responsibilities.")
            
        # Basic impact optimization template
        bullet_points = []
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith(('-', '*', '•')) or (len(line) > 15 and any(line.startswith(verb) for verb in ['Developed', 'Managed', 'Led', 'Created', 'Designed', 'Responsible', 'Worked'])):
                cleaned_line = re.sub(r'^[-*•]\s*', '', line).strip()
                if len(cleaned_line) > 20:
                    bullet_points.append(cleaned_line)
                    if len(bullet_points) >= 3:
                        break
                    
        impact_analysis = []
        default_bullets = [
            ("Responsible for writing code and debugging issues.", 
             "Uses passive 'responsible for' language and lacks quantifiable impact metrics.", 
             "Engineered and debugged core features, reducing system latency by 15% and resolving 40+ critical bugs."),
            ("Managed a team of developers to build web apps.",
             "Vague description that does not specify team size, technologies, or business outcomes.",
             "Led a cross-functional team of 6 engineers to deliver 3 high-scale web applications using React and Node.js, boosting user engagement by 25%.")
        ]
        
        if bullet_points:
            for bp in bullet_points:
                impact_analysis.append({
                    "original": bp,
                    "critique": "Lacks specific quantifiable metrics (percentages, dollar values, time savings) and strong action verbs.",
                    "optimized": f"Architected and optimized key components using industry best practices, resulting in a 20% increase in operational efficiency."
                })
        
        if not impact_analysis:
            for orig, crit, opt in default_bullets:
                impact_analysis.append({
                    "original": orig,
                    "critique": crit,
                    "optimized": opt
                })
                
        # Calculate score dynamically depending on whether Job Description is provided
        if job_description:
            jd_words = set(re.findall(r'\b\w+\b', job_description.lower()))
            resume_words = set(re.findall(r'\b\w+\b', text.lower()))
            
            # Find technical keywords present in JD
            jd_skills = [s for s in self.skills_keywords if s.lower() in jd_words]
            if jd_skills:
                matching_skills = [s for s in jd_skills if s.title() in skills]
                skill_match_ratio = len(matching_skills) / len(jd_skills)
            else:
                skill_match_ratio = 0.5 # Default fallback
                
            # Generic word overlap
            important_jd_words = jd_words - self.stop_words
            important_res_words = resume_words - self.stop_words
            overlap = important_jd_words.intersection(important_res_words)
            overlap_ratio = len(overlap) / max(1, len(important_jd_words))
            
            # Combine skill match and word overlap
            match_score = int((skill_match_ratio * 70) + (overlap_ratio * 30))
            score = max(10, min(100, match_score))
        else:
            completeness = sum(1 for v in sections.values() if v) / 7.0
            score = int(45 + completeness * 35 + (min(len(skills), 10) / 10.0) * 15)
            if score > 98: 
                score = 98

        # Dynamic Strategic Advice based on Score and Job Description
        advice_steps = []
        if job_description:
            advice_steps.append(f"1. **Match Score: {score}%**: Your resume currently has a {score}% match alignment with the target job description.")
            if score < 60:
                advice_steps.append("2. **Add Target Keywords**: Incorporate critical missing technical terms (such as: " + ", ".join(missing_kw[:3]) + ") into your experience bullet points to satisfy ATS filters.")
                advice_steps.append("3. **Highlight Core Skills**: Move your skills section to the top of your resume and group them by domain to align with the job requirements.")
            elif score < 80:
                advice_steps.append("2. **Refine Context Alignment**: You have many overlapping keywords, but you need to detail *how* you used these skills. Rewrite bullet points to state the exact context.")
                advice_steps.append("3. **Quantify Projects**: Add percentages, time-savings, or budget sizes to your projects page to demonstrate high-level business alignment.")
            else:
                advice_steps.append("2. **Tailor Profile Summary**: Tailor your headline/summary paragraph to exactly match the title of the target position.")
                advice_steps.append("3. **Ready to Apply**: Your resume is highly compatible with this role. Prepare behavioral interview stories highlighting these skills.")
        else:
            advice_steps.append(f"1. **General Score: {score}%**: Based on structure and content parsing, your resume strength is rated at {score}%.")
            if score < 60:
                advice_steps.append("2. **Complete Sections**: Add missing core sections like a Professional Summary or Certifications to achieve standard formatting structure.")
                advice_steps.append("3. **Expand Tech Stack**: List more technical tools, languages, or workflows you have worked with to improve keyword depth.")
            elif score < 80:
                advice_steps.append("2. **Deploy Action Verbs**: Start every experience bullet point with strong action verbs (e.g. 'Architected', 'Spearheaded', 'Optimized') rather than 'Responsible for'.")
                advice_steps.append("3. **Include Metrics**: Integrate quantifiable results (such as latency reduction, team size managed, or user growth) to prove business value.")
            else:
                advice_steps.append("2. **Tailor for Target Roles**: This is a very strong general resume. Make sure to paste a target Job Description to simulate a direct ATS matching alignment.")
                advice_steps.append("3. **Configure Cloud AI**: Add a `GEMINI_API_KEY` to your environment variables to get a deep semantic executive summary and AI-powered bullet-point optimizer.")

        advice = "\n".join(advice_steps)
        
        return {
            "summary": "This is a local heuristics analysis of your resume. You have strong foundations in " + (", ".join(skills[:3]) if skills else "technical fields") + ". To unlock a full generative AI executive summary, please configure a Gemini or Grok API key.",
            "ats_compatibility": {
                "score": score,
                "missing_keywords": missing_kw[:5],
                "formatting_issues": formatting_issues if formatting_issues else ["None identified by local parser."]
            },
            "impact_analysis": impact_analysis[:3],
            "skills_categorization": skills_cat,
            "strategic_advice": advice
        }

    def _extract_sections(self, text):
        """Identify resume sections"""
        sections = {
            'contact': False,
            'summary': False,
            'experience': False,
            'education': False,
            'skills': False,
            'projects': False,
            'certifications': False
        }
        
        text_lower = text.lower()
        
        # Check for section headers
        section_patterns = {
            'contact': r'(contact|phone|email|address|linkedin|github)',
            'summary': r'(summary|objective|profile|about)',
            'experience': r'(experience|work history|employment|professional experience)',
            'education': r'(education|academic|qualification)',
            'skills': r'(skills|technical skills|competencies)',
            'projects': r'(projects|portfolio)',
            'certifications': r'(certifications|certificates|licenses)'
        }
        
        for section, pattern in section_patterns.items():
            if re.search(pattern, text_lower):
                sections[section] = True
        
        return sections

    def _extract_entities(self, text):
        """Extract named entities using spaCy or regex"""
        entities = {
            'emails': [],
            'phones': [],
            'urls': [],
            'dates': []
        }
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities['emails'] = re.findall(email_pattern, text)
        
        # Extract phone numbers
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        entities['phones'] = re.findall(phone_pattern, text)
        
        # Extract URLs
        url_pattern = r'https?://[^\s]+|www\.[^\s]+'
        entities['urls'] = re.findall(url_pattern, text)
        
        # Extract dates (years)
        date_pattern = r'\b(19|20)\d{2}\b'
        entities['dates'] = list(set(re.findall(date_pattern, text)))
        
        # Use spaCy for more advanced entity extraction if available
        if self.nlp:
            doc = self.nlp(text)
            orgs = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
            persons = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
            entities['organizations'] = list(set(orgs))
            entities['persons'] = list(set(persons))
        
        return entities

    def _extract_skills(self, text):
        """Extract technical skills"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skills_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill.title())
        
        # Also look for common skill patterns
        skill_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:developer|engineer|specialist|expert)',
            r'proficient in\s+([^,\n]+)',
            r'skilled in\s+([^,\n]+)'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found_skills.extend([m.strip() for m in matches])
        
        return list(set(found_skills))

    def _extract_education(self, text):
        """Extract education information"""
        education = {
            'degrees': [],
            'institutions': [],
            'mentioned': False
        }
        
        text_lower = text.lower()
        
        # Check if education section exists
        if any(keyword in text_lower for keyword in self.education_keywords):
            education['mentioned'] = True
        
        # Extract degree patterns
        degree_patterns = [
            r'\b(B\.?S\.?|B\.?A\.?|B\.?E\.?|B\.?Tech|Bachelor)',
            r'\b(M\.?S\.?|M\.?A\.?|M\.?E\.?|M\.?Tech|Master)',
            r'\b(Ph\.?D\.?|Doctorate|PhD)'
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            education['degrees'].extend(matches)
        
        return education

    def _extract_experience(self, text):
        """Extract work experience information"""
        experience = {
            'years_mentioned': False,
            'positions': [],
            'companies': []
        }
        
        text_lower = text.lower()
        
        # Check for years of experience
        years_pattern = r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|exp)'
        if re.search(years_pattern, text_lower):
            experience['years_mentioned'] = True
        
        # Extract years
        years_matches = re.findall(years_pattern, text_lower)
        if years_matches:
            experience['years'] = [int(y) for y in years_matches]
        
        # Extract job titles (basic pattern)
        title_patterns = [
            r'(?:Senior|Junior|Lead|Principal)?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Developer|Engineer|Manager|Analyst|Specialist|Consultant)',
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, text)
            experience['positions'].extend([m.strip() for m in matches])
        
        return experience

    def _calculate_scores(self, text, sections, skills, education, experience):
        """Calculate various quality scores"""
        scores = {}
        
        # Completeness score (based on sections present)
        section_count = sum(1 for v in sections.values() if v)
        scores['completeness'] = min(100, (section_count / len(sections)) * 100)
        
        # Skills score
        skills_count = len(skills)
        scores['skills'] = min(100, (skills_count / 10) * 100)
        
        # Education score
        scores['education'] = 100 if education['mentioned'] else 50
        
        # Experience score
        scores['experience'] = 100 if experience['years_mentioned'] else 50
        
        # Readability score
        readability = flesch_reading_ease(text)
        scores['readability'] = max(0, min(100, readability))
        
        # Length score (optimal: 400-800 words)
        word_count = len(word_tokenize(text))
        if 400 <= word_count <= 800:
            scores['length'] = 100
        elif word_count < 400:
            scores['length'] = (word_count / 400) * 100
        else:
            scores['length'] = max(0, 100 - ((word_count - 800) / 400) * 50)
        
        return scores

    def _generate_suggestions(self, text, sections, skills, education, experience, scores):
        """Generate improvement suggestions"""
        suggestions = []
        
        # Section suggestions
        missing_sections = [k for k, v in sections.items() if not v]
        if missing_sections:
            suggestions.append({
                'type': 'section',
                'priority': 'high',
                'message': f"Consider adding: {', '.join(missing_sections).title()} section"
            })
        
        # Skills suggestions
        if len(skills) < 5:
            suggestions.append({
                'type': 'skills',
                'priority': 'high',
                'message': 'Add more technical skills to showcase your expertise'
            })
        
        # Length suggestions
        word_count = len(word_tokenize(text))
        if word_count < 300:
            suggestions.append({
                'type': 'length',
                'priority': 'medium',
                'message': 'Resume seems too short. Consider adding more details about your experience and achievements'
            })
        elif word_count > 1000:
            suggestions.append({
                'type': 'length',
                'priority': 'medium',
                'message': 'Resume is quite long. Consider condensing to keep it concise and impactful'
            })
        
        # Readability suggestions
        if scores['readability'] < 50:
            suggestions.append({
                'type': 'readability',
                'priority': 'medium',
                'message': 'Improve readability by using simpler language and shorter sentences'
            })
        
        # Experience suggestions
        if not experience['years_mentioned']:
            suggestions.append({
                'type': 'experience',
                'priority': 'high',
                'message': 'Mention years of experience to highlight your expertise'
            })
        
        return suggestions

    def _calculate_overall_rating(self, scores):
        """Calculate overall rating"""
        weights = {
            'completeness': 0.25,
            'skills': 0.25,
            'experience': 0.20,
            'education': 0.15,
            'readability': 0.10,
            'length': 0.05
        }
        
        overall = sum(scores.get(key, 0) * weight for key, weight in weights.items())
        
        if overall >= 90:
            rating = 'Excellent'
        elif overall >= 75:
            rating = 'Good'
        elif overall >= 60:
            rating = 'Fair'
        else:
            rating = 'Needs Improvement'
        
        return {
            'score': round(overall, 2),
            'rating': rating
        }
