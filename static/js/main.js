document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('scraperForm');
    const submitBtn = document.getElementById('submitBtn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const summary = document.getElementById('summary');
    const script = document.getElementById('script');
    const buttonText = submitBtn.querySelector('.button-text');
    const copyBtn = document.getElementById('copyBtn');

    // Add loading message elements
    const loadingMessage = document.createElement('p');
    loadingMessage.className = 'loading-status';
    loading.appendChild(loadingMessage);

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Reset previous results
        summary.textContent = '';
        script.textContent = '';
        
        // Update UI state
        submitBtn.disabled = true;
        buttonText.textContent = 'Processing...';
        loading.classList.remove('hidden');
        results.classList.add('hidden');
        loadingMessage.textContent = 'Scraping website content...';

        try {
            const response = await fetch('/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: form.url.value,
                    model: form.model.value,
                    prompt: form.prompt.value
                })
            });

            const data = await response.json();
            
            if (data.success && data.summary && data.script) {
                // Update content with proper formatting
                summary.innerHTML = formatContent(data.summary);
                script.innerHTML = formatContent(data.script);
                results.classList.remove('hidden');
            } else {
                throw new Error(data.error || 'Failed to generate content');
            }
        } catch (error) {
            showError(error.message);
        } finally {
            submitBtn.disabled = false;
            buttonText.textContent = 'Generate Script';
            loading.classList.add('hidden');
        }
    });

    function formatContent(text) {
        // Convert line breaks to HTML and escape HTML entities
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>'); // Bold text between **
    }

    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `
            <div class="error-content">
                <svg class="error-icon" viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                </svg>
                <span>${message}</span>
            </div>
        `;
        
        // Add error styles
        const style = document.createElement('style');
        style.textContent = `
            .error-message {
                background-color: #fef2f2;
                border: 1px solid #fee2e2;
                border-radius: 8px;
                padding: 1rem;
                margin: 1rem 0;
                color: #991b1b;
            }
            .error-content {
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            .error-icon {
                width: 24px;
                height: 24px;
                fill: currentColor;
            }
        `;
        document.head.appendChild(style);
        
        // Insert error message
        results.insertAdjacentElement('beforebegin', errorDiv);
        
        // Remove after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    // Copy to clipboard functionality
    copyBtn.addEventListener('click', async () => {
        const scriptText = document.getElementById('script').textContent;
        try {
            await navigator.clipboard.writeText(scriptText);
            
            // Update button text temporarily
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = '<span class="button-text">Copied! ✓</span>';
            copyBtn.classList.add('success');
            
            // Reset button after 2 seconds
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
                copyBtn.classList.remove('success');
            }, 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
            copyBtn.innerHTML = '<span class="button-text">Failed to copy</span>';
            copyBtn.classList.add('error');
            
            setTimeout(() => {
                copyBtn.innerHTML = '<span class="button-text">Copy to Clipboard</span>';
                copyBtn.classList.remove('error');
            }, 2000);
        }
    });

    document.getElementById('downloadBtn').addEventListener('click', () => {
        const script = document.getElementById('script').textContent;
        const blob = new Blob([script], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        const timestamp = new Date().toISOString().split('T')[0];
        
        a.href = url;
        a.download = `generated-script-${timestamp}.txt`;
        a.click();
        
        window.URL.revokeObjectURL(url);
    });
});
