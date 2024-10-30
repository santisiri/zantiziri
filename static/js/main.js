document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('scraperForm');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const summary = document.getElementById('summary');
    const script = document.getElementById('script');
    const submitBtn = document.getElementById('submitBtn');

    form?.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        try {
            // Show loading state
            loading.classList.remove('hidden');
            results.classList.add('hidden');
            submitBtn.disabled = true;

            // Get form data
            const formData = {
                url: document.getElementById('url').value,
                model: document.getElementById('model').value,
                prompt: document.getElementById('prompt').value
            };

            console.log('Sending request with data:', formData); // Debug log

            const response = await fetch('/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            console.log('Response status:', response.status); // Debug log

            // Check if response is JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Response was not JSON');
            }

            const data = await response.json();
            console.log('Response data:', data); // Debug log

            if (data.success) {
                summary.innerHTML = data.summary;
                script.innerHTML = data.script;
                results.classList.remove('hidden');
                
                // Generate initial image prompt based on summary
                if (window.imageGenerator) {
                    imageGenerator.generatePromptFromScript();
                }
                
                // Scroll to results
                results.scrollIntoView({ behavior: 'smooth' });
            } else {
                throw new Error(data.error || 'Failed to process request');
            }
        } catch (error) {
            console.error('Error:', error); // Debug log
            
            // Show error message to user
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = `Error: ${error.message}`;
            form.insertAdjacentElement('beforebegin', errorDiv);
            
            // Remove error message after 5 seconds
            setTimeout(() => errorDiv.remove(), 5000);
        } finally {
            loading.classList.add('hidden');
            submitBtn.disabled = false;
        }
    });
});
