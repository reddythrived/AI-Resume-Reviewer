const APP_URL = 'https://ai-resume-reviewer-production-e7b3.up.railway.app';

document.getElementById('openApp').addEventListener('click', () => {
  chrome.tabs.create({ url: APP_URL });
});
