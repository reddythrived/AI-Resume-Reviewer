// DOM Elements
const uploadForm = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');
const jdInput = document.getElementById('jdInput');
const textInput = document.getElementById('textInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const uploadSection = document.getElementById('uploadSection');
const resultsSection = document.getElementById('resultsSection');
const loadingStatus = document.getElementById('loadingStatus');

// Global Chart instance
let scoreChart = null;
let currentAnalysisData = null;

// File input handling
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        fileName.textContent = e.target.files[0].name;
        fileName.style.color = '#818cf8';
    } else {
        fileName.textContent = 'Choose file or drag & drop';
        fileName.style.color = '';
    }
});

// Form submission
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const file = fileInput.files[0];
    const text = textInput.value.trim();
    const jobDescription = jdInput.value.trim();
    
    if (!file && !text) {
        alert('Please upload a file or paste resume text');
        return;
    }
    
    showLoading();
    
    try {
        let response;
        const formData = new FormData();
        if (jobDescription) formData.append('job_description', jobDescription);

        if (file) {
            formData.append('file', file);
            response = await fetch('/api/analyze', { method: 'POST', body: formData });
        } else {
            response = await fetch('/api/analyze-text', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text, job_description: jobDescription })
            });
        }
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Analysis failed');
        }
        
        const data = await response.json();
        currentAnalysisData = data;
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error analyzing resume: ' + error.message);
        hideLoading();
    }
});

function showLoading() {
    loading.style.display = 'block';
    analyzeBtn.disabled = true;
    const statuses = [
        "Scanning document structure...",
        "Extracting biometric skill markers...",
        "Simulating ATS compatibility...",
        "Generating semantic improvements...",
        "Finalizing diagnostic report..."
    ];
    let i = 0;
    const interval = setInterval(() => {
        if (loading.style.display === 'none') {
            clearInterval(interval);
            return;
        }
        loadingStatus.textContent = statuses[i % statuses.length];
        i++;
    }, 1500);
}

function hideLoading() {
    loading.style.display = 'none';
    analyzeBtn.disabled = false;
}

function renderScoreChart(score) {
    const canvas = document.getElementById('scoreChart');
    const ctx = canvas.getContext('2d');
    if (scoreChart) scoreChart.destroy();
    
    // Create gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, '#6366f1');
    gradient.addColorStop(1, '#a855f7');

    scoreChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [gradient, 'rgba(255, 255, 255, 0.03)'],
                borderWidth: 0,
                borderRadius: 20,
            }]
        },
        options: {
            cutout: '85%',
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 2000,
                easing: 'easeOutQuart'
            },
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            }
        }
    });
}

function displayResults(data) {
    hideLoading();
    
    // Smooth transition sequence
    uploadSection.style.opacity = '0';
    uploadSection.style.transform = 'scale(0.95)';
    uploadSection.style.transition = 'all 0.4s ease';
    
    setTimeout(() => {
        uploadSection.style.display = 'none';
        resultsSection.style.display = 'block';
        resultsSection.style.opacity = '0';
        resultsSection.style.transform = 'translateY(30px)';
        
        // Trigger reflow
        resultsSection.offsetHeight;
        
        resultsSection.style.transition = 'all 0.8s cubic-bezier(0.2, 0.8, 0.2, 1)';
        resultsSection.style.opacity = '1';
        resultsSection.style.transform = 'translateY(0)';
        
        // Update stats with delay for effect
        document.getElementById('wordCount').textContent = data.statistics.word_count.toLocaleString();
        document.getElementById('readabilityScore').textContent = Math.round(data.statistics.readability_score);
        document.getElementById('skillsCount').textContent = data.skills.length;

        const overallScore = data.ai_analysis ? data.ai_analysis.ats_compatibility.score : data.overall_rating.score;
        renderScoreChart(overallScore);
        animateValue("overallScore", 0, Math.round(overallScore), 2000);
        document.getElementById('atsScore').textContent = Math.round(overallScore) + "%";
        
        const ratingBadge = document.getElementById('ratingBadge');
        const rating = data.overall_rating.rating;
        ratingBadge.textContent = rating;
        ratingBadge.className = 'rating-badge ' + rating.toLowerCase().replace(' ', '-');

        if (data.ai_analysis) renderAIAnalysis(data.ai_analysis);
        updateScoreBreakdown(data.scores);
        
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 400);
}

function animateValue(id, start, end, duration) {
    const obj = document.getElementById(id);
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

function renderAIAnalysis(ai) {
    // Summary
    document.getElementById('aiSummary').textContent = ai.summary;

    // Missing Keywords
    const keywordsContainer = document.getElementById('missingKeywords');
    keywordsContainer.innerHTML = '';
    if (ai.ats_compatibility.missing_keywords && ai.ats_compatibility.missing_keywords.length > 0) {
        ai.ats_compatibility.missing_keywords.forEach(kw => {
            const span = document.createElement('span');
            span.className = 'keyword-tag';
            span.textContent = kw;
            keywordsContainer.appendChild(span);
        });
    } else {
        keywordsContainer.innerHTML = '<p class="success-text">Perfect! No critical keywords missing.</p>';
    }

    // Formatting Issues
    const issuesContainer = document.getElementById('formattingIssues');
    issuesContainer.innerHTML = '';
    if (ai.ats_compatibility.formatting_issues) {
        ai.ats_compatibility.formatting_issues.forEach(issue => {
            const div = document.createElement('div');
            div.className = 'issue-item';
            div.style.padding = '10px 0';
            div.innerHTML = `<i class="fas fa-times-circle" style="color: #ef4444; margin-right: 10px;"></i> ${issue}`;
            issuesContainer.appendChild(div);
        });
    }

    // Impact Analysis
    const impactList = document.getElementById('impactList');
    impactList.innerHTML = '';
    if (ai.impact_analysis) {
        ai.impact_analysis.forEach(item => {
            const div = document.createElement('div');
            div.className = 'impact-item';
            div.innerHTML = `
                <div class="impact-original">"${item.original}"</div>
                <div class="impact-critique"><i class="fas fa-info-circle"></i> ${item.critique}</div>
                <div class="impact-optimized"><i class="fas fa-check-circle"></i> ${item.optimized}</div>
            `;
            impactList.appendChild(div);
        });
    }

    // Skills Categorization
    const skillsContainer = document.getElementById('skillsCategories');
    skillsContainer.innerHTML = '';
    if (ai.skills_categorization) {
        for (const [category, skills] of Object.entries(ai.skills_categorization)) {
            if (skills.length === 0) continue;
            const group = document.createElement('div');
            group.className = 'skill-group';
            group.innerHTML = `
                <h4>${category}</h4>
                <div class="skills-list" style="display: flex; flex-wrap: wrap; gap: 8px;">${skills.map(s => `<span class="skill-tag">${s}</span>`).join('')}</div>
            `;
            skillsContainer.appendChild(group);
        }
    }

    // Strategic Advice
    document.getElementById('strategicAdvice').innerHTML = `<p style="line-height: 1.6;">${ai.strategic_advice}</p>`;
}

function updateScoreBreakdown(scores) {
    const scoreItems = document.getElementById('scoreItems');
    scoreItems.innerHTML = '';
    const scoreLabels = {
        completeness: { label: 'Completeness', icon: 'fas fa-check-circle' },
        skills: { label: 'Technical Skills', icon: 'fas fa-tools' },
        experience: { label: 'Work History', icon: 'fas fa-briefcase' },
        readability: { label: 'Readability', icon: 'fas fa-book-reader' }
    };
    
    for (const [key, value] of Object.entries(scores)) {
        if (scoreLabels[key]) {
            const div = document.createElement('div');
            div.className = 'score-item';
            div.style.marginBottom = '10px';
            div.innerHTML = `
                <div class="score-item-label" style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
                    <i class="${scoreLabels[key].icon}" style="color: #6366f1;"></i> ${scoreLabels[key].label}
                </div>
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div class="score-bar-wrapper" style="flex: 1; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
                        <div class="score-bar" style="width: ${value}%; height: 100%; background: linear-gradient(90deg, #6366f1, #a855f7); border-radius: 4px;"></div>
                    </div>
                    <div class="score-item-value" style="font-weight: 700; min-width: 40px;">${Math.round(value)}%</div>
                </div>
            `;
            scoreItems.appendChild(div);
        }
    }
}

function resetAnalysis() {
    resultsSection.style.display = 'none';
    uploadSection.style.display = 'block';
    uploadForm.reset();
    fileName.textContent = 'Choose file or drag & drop';
    fileName.style.color = '';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function downloadReport() {
    window.print();
}

function generateReport() {
    if (!currentAnalysisData) return 'No data';
    const d = currentAnalysisData;
    const ai = d.ai_analysis;
    
    let report = `AI RESUME DIAGNOSTIC REPORT\n===========================\n\n`;
    report += `SUMMARY: ${ai ? ai.summary : 'N/A'}\n\n`;
    report += `ATS COMPATIBILITY SCORE: ${ai ? ai.ats_compatibility.score : d.overall_rating.score}%\n`;
    if (ai) {
        report += `MISSING KEYWORDS: ${ai.ats_compatibility.missing_keywords.join(', ')}\n`;
        report += `FORMATTING ISSUES: ${ai.ats_compatibility.formatting_issues.join(', ')}\n\n`;
        report += `STRATEGIC ADVICE:\n${ai.strategic_advice}\n`;
    }
    return report;
}
