// DOM Elements
const uploadForm = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');
const textInput = document.getElementById('textInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const uploadSection = document.getElementById('uploadSection');
const resultsSection = document.getElementById('resultsSection');

// Store analysis data globally
let currentAnalysisData = null;

// File input handling
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        fileName.textContent = e.target.files[0].name;
        fileName.style.color = '#6366f1';
    } else {
        fileName.textContent = 'Choose file or drag & drop';
        fileName.style.color = '';
    }
});

// Drag and drop
const fileLabel = document.querySelector('.file-label');
fileLabel.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileLabel.style.borderColor = '#6366f1';
    fileLabel.style.background = 'rgba(99, 102, 241, 0.15)';
});

fileLabel.addEventListener('dragleave', () => {
    fileLabel.style.borderColor = '#334155';
    fileLabel.style.background = 'rgba(99, 102, 241, 0.05)';
});

fileLabel.addEventListener('drop', (e) => {
    e.preventDefault();
    fileLabel.style.borderColor = '#334155';
    fileLabel.style.background = 'rgba(99, 102, 241, 0.05)';
    
    if (e.dataTransfer.files.length > 0) {
        fileInput.files = e.dataTransfer.files;
        fileName.textContent = e.dataTransfer.files[0].name;
        fileName.style.color = '#6366f1';
    }
});

// Form submission
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const file = fileInput.files[0];
    const text = textInput.value.trim();
    
    if (!file && !text) {
        alert('Please upload a file or paste resume text');
        return;
    }
    
    showLoading();
    
    try {
        let response;
        
        if (file) {
            // Upload file
            const formData = new FormData();
            formData.append('file', file);
            
            response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });
        } else {
            // Analyze text
            response = await fetch('/api/analyze-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            });
        }
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Analysis failed');
        }
        
        const data = await response.json();
        currentAnalysisData = data; // Store for report generation
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error analyzing resume: ' + error.message);
        hideLoading();
    }
});

// Show loading state
function showLoading() {
    loading.style.display = 'block';
    analyzeBtn.disabled = true;
    analyzeBtn.style.opacity = '0.6';
    analyzeBtn.style.cursor = 'not-allowed';
}

// Hide loading state
function hideLoading() {
    loading.style.display = 'none';
    analyzeBtn.disabled = false;
    analyzeBtn.style.opacity = '1';
    analyzeBtn.style.cursor = 'pointer';
}

// Display results
function displayResults(data) {
    hideLoading();
    
    // Hide upload section, show results
    uploadSection.style.display = 'none';
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Update statistics
    updateStatistics(data.statistics);
    
    // Update overall rating
    updateOverallRating(data.overall_rating, data.scores);
    
    // Update score breakdown
    updateScoreBreakdown(data.scores);
    
    // Update skills
    updateSkills(data.skills);
    
    // Update sections
    updateSections(data.sections);
    
    // Update suggestions
    updateSuggestions(data.suggestions);
}

// Update statistics
function updateStatistics(stats) {
    document.getElementById('wordCount').textContent = stats.word_count.toLocaleString();
    document.getElementById('sentenceCount').textContent = stats.sentence_count;
    document.getElementById('readabilityScore').textContent = Math.round(stats.readability_score);
    document.getElementById('skillsCount').textContent = document.querySelectorAll('.skill-tag').length || 0;
}

// Update overall rating
function updateOverallRating(rating, scores) {
    const score = rating.score;
    const ratingText = rating.rating;
    
    // Update score circle
    const circle = document.getElementById('scoreCircle');
    const circumference = 2 * Math.PI * 85;
    const offset = circumference - (score / 100) * circumference;
    circle.style.strokeDashoffset = offset;
    
    // Update score text
    document.getElementById('overallScore').textContent = Math.round(score);
    
    // Update rating badge
    const ratingBadge = document.getElementById('ratingBadge');
    ratingBadge.textContent = ratingText;
    ratingBadge.className = 'rating-badge ' + ratingText.toLowerCase().replace(' ', '-');
}

// Update score breakdown
function updateScoreBreakdown(scores) {
    const scoreItems = document.getElementById('scoreItems');
    scoreItems.innerHTML = '';
    
    const scoreLabels = {
        completeness: { label: 'Completeness', icon: 'fas fa-check-circle' },
        skills: { label: 'Skills', icon: 'fas fa-tools' },
        experience: { label: 'Experience', icon: 'fas fa-briefcase' },
        education: { label: 'Education', icon: 'fas fa-graduation-cap' },
        readability: { label: 'Readability', icon: 'fas fa-book-reader' },
        length: { label: 'Length', icon: 'fas fa-ruler' }
    };
    
    for (const [key, value] of Object.entries(scores)) {
        if (scoreLabels[key]) {
            const item = document.createElement('div');
            item.className = 'score-item';
            
            const roundedScore = Math.round(value);
            const color = getScoreColor(value);
            
            item.innerHTML = `
                <div class="score-item-label">
                    <i class="${scoreLabels[key].icon}"></i>
                    <span>${scoreLabels[key].label}</span>
                </div>
                <div class="score-bar-wrapper">
                    <div class="score-bar" style="width: ${value}%; background: ${color};"></div>
                </div>
                <div class="score-item-value" style="color: ${color};">
                    ${roundedScore}%
                </div>
            `;
            
            scoreItems.appendChild(item);
        }
    }
}

// Get color based on score
function getScoreColor(score) {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#6366f1';
    if (score >= 40) return '#f59e0b';
    return '#ef4444';
}

// Update skills
function updateSkills(skills) {
    const skillsContainer = document.getElementById('skillsContainer');
    skillsContainer.innerHTML = '';
    
    if (skills.length === 0) {
        skillsContainer.innerHTML = '<p style="color: var(--text-secondary);">No skills detected</p>';
        return;
    }
    
    skills.forEach(skill => {
        const tag = document.createElement('span');
        tag.className = 'skill-tag';
        tag.textContent = skill;
        skillsContainer.appendChild(tag);
    });
    
    // Update skills count in statistics
    document.getElementById('skillsCount').textContent = skills.length;
}

// Update sections
function updateSections(sections) {
    const sectionsGrid = document.getElementById('sectionsGrid');
    sectionsGrid.innerHTML = '';
    
    const sectionLabels = {
        contact: 'Contact Information',
        summary: 'Summary/Objective',
        experience: 'Work Experience',
        education: 'Education',
        skills: 'Skills',
        projects: 'Projects',
        certifications: 'Certifications'
    };
    
    for (const [key, present] of Object.entries(sections)) {
        const item = document.createElement('div');
        item.className = `section-item ${present ? 'present' : 'missing'}`;
        
        item.innerHTML = `
            <i class="fas ${present ? 'fa-check-circle' : 'fa-times-circle'}"></i>
            <span>${sectionLabels[key] || key}</span>
        `;
        
        sectionsGrid.appendChild(item);
    }
}

// Update suggestions
function updateSuggestions(suggestions) {
    const suggestionsList = document.getElementById('suggestionsList');
    suggestionsList.innerHTML = '';
    
    if (suggestions.length === 0) {
        suggestionsList.innerHTML = '<p style="color: var(--text-secondary); padding: 1rem;">Great job! Your resume looks excellent.</p>';
        return;
    }
    
    suggestions.forEach(suggestion => {
        const item = document.createElement('div');
        item.className = `suggestion-item ${suggestion.priority}`;
        
        item.innerHTML = `
            <i class="fas fa-lightbulb"></i>
            <div class="suggestion-content">
                <div class="suggestion-type">${suggestion.type.toUpperCase()} - ${suggestion.priority.toUpperCase()}</div>
                <div class="suggestion-message">${suggestion.message}</div>
            </div>
        `;
        
        suggestionsList.appendChild(item);
    });
}

// Reset analysis
function resetAnalysis() {
    uploadSection.style.display = 'block';
    resultsSection.style.display = 'none';
    uploadForm.reset();
    fileName.textContent = 'Choose file or drag & drop';
    fileName.style.color = '';
    textInput.value = '';
    currentAnalysisData = null; // Clear stored data
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Download report
function downloadReport() {
    if (!currentAnalysisData) {
        alert('No analysis data available. Please analyze a resume first.');
        return;
    }
    
    try {
        // Generate comprehensive report
        const report = generateReport();
        const blob = new Blob([report], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `resume-analysis-report-${new Date().getTime()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error downloading report:', error);
        alert('Error generating report. Please try again.');
    }
}

// Generate comprehensive report
function generateReport() {
    if (!currentAnalysisData) {
        return 'No analysis data available.';
    }
    
    const data = currentAnalysisData;
    const overallScore = Math.round(data.overall_rating.score);
    const rating = data.overall_rating.rating;
    const stats = data.statistics;
    const scores = data.scores;
    
    let report = `╔══════════════════════════════════════════════════════════════╗
║           AI RESUME ANALYSIS REPORT                      ║
╚══════════════════════════════════════════════════════════════╝

Generated: ${new Date().toLocaleString()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OVERALL RATING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Score: ${overallScore}/100
Rating: ${rating}

STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Word Count:        ${stats.word_count.toLocaleString()}
Character Count:  ${stats.char_count.toLocaleString()}
Sentence Count:   ${stats.sentence_count}
Readability Score: ${Math.round(stats.readability_score)}/100

SCORE BREAKDOWN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Completeness:     ${Math.round(scores.completeness)}%
Skills:           ${Math.round(scores.skills)}%
Experience:       ${Math.round(scores.experience)}%
Education:        ${Math.round(scores.education)}%
Readability:      ${Math.round(scores.readability)}%
Length:           ${Math.round(scores.length)}%

RESUME SECTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Contact Information:     ${data.sections.contact ? '✓ Present' : '✗ Missing'}
Summary/Objective:       ${data.sections.summary ? '✓ Present' : '✗ Missing'}
Work Experience:          ${data.sections.experience ? '✓ Present' : '✗ Missing'}
Education:               ${data.sections.education ? '✓ Present' : '✗ Missing'}
Skills:                  ${data.sections.skills ? '✓ Present' : '✗ Missing'}
Projects:                ${data.sections.projects ? '✓ Present' : '✗ Missing'}
Certifications:          ${data.sections.certifications ? '✓ Present' : '✗ Missing'}

DETECTED SKILLS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`;

    if (data.skills && data.skills.length > 0) {
        data.skills.forEach((skill, index) => {
            report += `${index + 1}. ${skill}\n`;
        });
    } else {
        report += 'No skills detected.\n';
    }
    
    report += `\nIMPROVEMENT SUGGESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`;

    if (data.suggestions && data.suggestions.length > 0) {
        data.suggestions.forEach((suggestion, index) => {
            report += `\n${index + 1}. [${suggestion.priority.toUpperCase()}] ${suggestion.type.toUpperCase()}\n`;
            report += `   ${suggestion.message}\n`;
        });
    } else {
        report += 'Great job! Your resume looks excellent.\n';
    }
    
    if (data.entities) {
        report += `\nDETECTED ENTITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`;
        if (data.entities.emails && data.entities.emails.length > 0) {
            report += `Emails: ${data.entities.emails.join(', ')}\n`;
        }
        if (data.entities.phones && data.entities.phones.length > 0) {
            report += `Phone Numbers: ${data.entities.phones.length} found\n`;
        }
        if (data.entities.urls && data.entities.urls.length > 0) {
            report += `URLs: ${data.entities.urls.join(', ')}\n`;
        }
        if (data.entities.organizations && data.entities.organizations.length > 0) {
            report += `Organizations: ${data.entities.organizations.join(', ')}\n`;
        }
    }
    
    report += `\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Report generated by AI Resume Analyzer
Powered by NLP & Machine Learning
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`;
    
    return report;
}
