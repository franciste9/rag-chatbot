const API_URL = 'http://localhost:5001/api';

async function uploadFile() {
    const file = document.getElementById('fileInput').files[0];
    if (!file) {
        alert('Please select a file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.innerHTML = '⏳ Uploading...';
    
    try {
        const response = await fetch(`${API_URL}/documents/upload`, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        if (response.ok) {
            statusDiv.innerHTML = `✅ <strong>Success!</strong> Uploaded: <strong>${data.num_chunks}</strong> chunks from "${data.filename}"`;
        } else {
            statusDiv.innerHTML = `❌ Error: ${data.error}`;
        }
    } catch (error) {
        statusDiv.innerHTML = `❌ Error: ${error.message}`;
    }
}

async function chat() {
    const query = document.getElementById('queryInput').value;
    if (!query.trim()) {
        alert('Please enter a question');
        return;
    }
    
    const resultDiv = document.getElementById('chatResult');
    resultDiv.innerHTML = '⏳ Thinking...';
    resultDiv.style.display = 'block';
    
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        const data = await response.json();
        
        if (response.ok) {
            let html = `<strong>Q:</strong><p>${escapeHtml(data.query)}</p>`;
            html += `<strong>A:</strong><p>${escapeHtml(data.answer)}</p>`;
            
            if (data.sources && data.sources.length > 0) {
                html += '<div class="sources"><strong>📚 Sources:</strong>';
                data.sources.forEach((source, i) => {
                    html += `<div class="source-item">${i+1}. ${escapeHtml(source.text.substring(0, 100))}... (score: ${source.score.toFixed(3)})</div>`;
                });
                html += '</div>';
            }
            
            resultDiv.innerHTML = html;
        } else {
            resultDiv.innerHTML = `❌ Error: ${data.error}`;
        }
    } catch (error) {
        resultDiv.innerHTML = `❌ Error: ${error.message}`;
    }
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Allow Enter key in textarea
document.addEventListener('DOMContentLoaded', () => {
    const queryInput = document.getElementById('queryInput');
    queryInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            chat();
        }
    });
});
