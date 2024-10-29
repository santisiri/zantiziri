class ImageGenerator {
    constructor() {
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const generateBtn = document.getElementById('generateImage');
        const regeneratePromptBtn = document.getElementById('regeneratePrompt');
        const downloadBtn = document.getElementById('downloadImages');
        const regenerateBtn = document.getElementById('regenerateImages');

        generateBtn?.addEventListener('click', () => this.generateImages());
        regeneratePromptBtn?.addEventListener('click', () => this.regeneratePrompt());
        downloadBtn?.addEventListener('click', () => this.downloadAllImages());
        regenerateBtn?.addEventListener('click', () => this.generateImages());
    }

    async generatePromptFromScript() {
        const scriptText = document.getElementById('script').textContent;
        try {
            const response = await fetch('/generate-image-prompt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ script: scriptText })
            });

            const data = await response.json();
            if (data.success) {
                document.getElementById('imagePrompt').value = data.prompt;
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.showError('Failed to generate image prompt: ' + error.message);
        }
    }

    async generateImages() {
        const prompt = document.getElementById('imagePrompt').value;
        const style = document.getElementById('imageStyle').value;

        if (!prompt) {
            this.showError('Please enter an image description');
            return;
        }

        try {
            this.showProgress();
            const response = await fetch('/generate-images', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt,
                    style,
                    count: 4
                })
            });

            const data = await response.json();
            if (data.success) {
                this.displayImages(data.images);
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.showError('Failed to generate images: ' + error.message);
        } finally {
            this.hideProgress();
        }
    }

    displayImages(images) {
        const gallery = document.querySelector('.gallery-grid');
        gallery.innerHTML = '';

        images.forEach(image => {
            const imageContainer = document.createElement('div');
            imageContainer.className = 'gallery-image';
            imageContainer.innerHTML = `
                <img src="${image.url}" alt="${image.prompt}">
                <div class="image-overlay">
                    <button class="icon-button" onclick="imageGenerator.downloadImage('${image.url}')">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                            <polyline points="7 10 12 15 17 10"></polyline>
                            <line x1="12" y1="15" x2="12" y2="3"></line>
                        </svg>
                    </button>
                </div>
            `;
            gallery.appendChild(imageContainer);
        });

        document.querySelector('.image-gallery').classList.remove('hidden');
    }

    async downloadImage(imageUrl) {
        try {
            const response = await fetch('/download-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: imageUrl })
            });

            const data = await response.json();
            if (data.success) {
                // Create download link
                const link = document.createElement('a');
                link.href = `data:image/png;base64,${data.image}`;
                link.download = `generated-image-${Date.now()}.png`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.showError('Failed to download image: ' + error.message);
        }
    }

    async downloadAllImages() {
        const images = document.querySelectorAll('.gallery-image img');
        for (const image of images) {
            await this.downloadImage(image.src);
            // Add small delay between downloads
            await new Promise(resolve => setTimeout(resolve, 500));
        }
    }

    showProgress() {
        document.querySelector('.image-generation-progress').classList.remove('hidden');
        document.getElementById('generateImage').disabled = true;
    }

    hideProgress() {
        document.querySelector('.image-generation-progress').classList.add('hidden');
        document.getElementById('generateImage').disabled = false;
    }

    showError(message) {
        // Create error notification
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    regeneratePrompt() {
        this.generatePromptFromScript();
    }
}

// Initialize the image generator
const imageGenerator = new ImageGenerator();
