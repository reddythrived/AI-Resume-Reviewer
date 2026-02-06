import re
import os
import PyPDF2
from docx import Document
import spacy
import nltk
from textstat import flesch_reading_ease, syllable_count
from collections import Counter
import json

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
        # Try to load spaCy model, fallback to basic if not available
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Using basic NLP.")
            self.nlp = None
        
        self.stop_words = set(stopwords.words('english'))
        
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

    def analyze(self, filepath):
        """Analyze resume from file"""
        text = self.extract_text_from_file(filepath)
        return self.analyze_text(text)

    def analyze_text(self, text):
        """Comprehensive resume analysis"""
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
        
        return {
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
