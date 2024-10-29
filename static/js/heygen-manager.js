class HeyGenManager {
    constructor() {
        this.apiKey = null;
        this.selectedAvatar = null;
        this.videoGenerationId = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Modal handlers
        document.getElementById('generateVideoBtn')?.addEventListener('click', () => {
            this.showApiKeyModal();
        });

        document.querySelector('.close-button')?.addEventListener('click', () => {
            this.hideApiKeyModal();
        });

        document.getElementById('verifyApiKey')?.addEventListener('click', () => {
            this.verifyAndInitialize();
        });

        // Password visibility toggle
        const togglePassword = document.querySelector('.toggle-password');
        const apiKeyInput = document.getElementById('heygen-api-key');
        
        togglePassword?.addEventListener('click', () => {
            const type = apiKeyInput.getAttribute('type') === 'password' ? 'text' : 'password';
            apiKeyInput.setAttribute('type', type);
            
            // Update the eye icon
            const eyeIcon = togglePassword.querySelector('.eye-icon');
            if (type === 'password') {
                eyeIcon.innerHTML = `
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                `;
            } else {
                eyeIcon.innerHTML = `
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                    <line x1="1" y1="1" x2="23" y2="23"></line>
                `;
            }
        });
    }

    showApiKeyModal() {
        const modal = document.getElementById('apiKeyModal');
        modal.classList.remove('hidden');
        modal.classList.add('active');
        
        // Also show the HeyGen section
        document.getElementById('heygenSection').classList.remove('hidden');
        
        // Smooth scroll to HeyGen section
        document.getElementById('heygenSection').scrollIntoView({ behavior: 'smooth' });
    }

    hideApiKeyModal() {
        const modal = document.getElementById('apiKeyModal');
        modal.classList.remove('active');
        modal.classList.add('hidden');
    }

    async verifyApiKey(apiKey) {
        try {
            console.log('Sending API key verification request...'); // Debug log
            const response = await fetch('/verify-heygen-key', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ api_key: apiKey })
            });

            console.log('Received response:', response.status); // Debug log
            const data = await response.json();
            console.log('Response data:', data); // Debug log

            if (!data.success) {
                throw new Error(data.error || 'Invalid API key');
            }

            return true;
        } catch (error) {
            console.error('API key verification error:', error); // Debug log
            throw new Error(`Failed to verify API key: ${error.message}`);
        }
    }

    async verifyAndInitialize() {
        const apiKey = document.getElementById('heygen-api-key').value;
        if (!apiKey) {
            this.showError('Please enter an API key');
            return;
        }

        try {
            const isValid = await this.verifyApiKey(apiKey);
            if (isValid) {
                this.apiKey = apiKey;
                this.hideApiKeyModal();
                await this.initializeHeyGenSection();
            }
        } catch (error) {
            this.showError(error.message);
        }
    }

    async initializeHeyGenSection() {
        try {
            await this.loadAvatars();
            document.getElementById('avatar-section').classList.remove('hidden');
        } catch (error) {
            this.showError('Failed to initialize HeyGen section');
        }
    }

    async loadAvatars() {
        try {
            const response = await fetch('/get-heygen-avatars', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ api_key: this.apiKey })
            });

            const data = await response.json();
            if (data.success) {
                this.renderAvatars(data.avatars);
            } else {
                throw new Error(data.error || 'Failed to load avatars');
            }
        } catch (error) {
            this.showError('Failed to load avatars');
            throw error;
        }
    }

    renderAvatars(avatars) {
        const grid = document.querySelector('.avatar-grid');
        grid.innerHTML = avatars.map(avatar => `
            <div class="avatar-option" data-avatar-id="${avatar.id}">
                <img src="${avatar.thumbnail_url}" alt="${avatar.name}">
                <p>${avatar.name}</p>
            </div>
        `).join('');

        // Add click handlers to avatars
        grid.querySelectorAll('.avatar-option').forEach(avatar => {
            avatar.addEventListener('click', () => {
                this.selectAvatar(avatar);
            });
        });
    }

    selectAvatar(element) {
        document.querySelectorAll('.avatar-option').forEach(el => {
            el.classList.remove('selected');
        });
        element.classList.add('selected');
        this.selectedAvatar = element.dataset.avatarId;
        document.getElementById('startVideoGeneration').classList.remove('hidden');
    }

    showError(message) {
        console.error('Error:', message); // Debug log
        // Create and show error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        // Add styles for visibility
        errorDiv.style.backgroundColor = '#fee2e2';
        errorDiv.style.color = '#dc2626';
        errorDiv.style.padding = '1rem';
        errorDiv.style.borderRadius = '0.375rem';
        errorDiv.style.marginBottom = '1rem';
        
        // Insert error message at the top of the HeyGen section
        const heygenSection = document.getElementById('heygenSection');
        heygenSection.insertAdjacentElement('afterbegin', errorDiv);
        
        // Remove error message after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    async createVideo(script) {
        if (!this.selectedAvatar) {
            this.showError('Please select an avatar first');
            return;
        }

        try {
            const response = await fetch('/create-heygen-video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    api_key: this.apiKey,
                    avatar_id: this.selectedAvatar,
                    script: script
                })
            });

            const data = await response.json();
            if (data.success) {
                this.videoGenerationId = data.video_id;
                this.showProgressBar();
                await this.monitorProgress();
            } else {
                throw new Error(data.error || 'Failed to start video generation');
            }
        } catch (error) {
            this.showError(error.message);
        }
    }

    showProgressBar() {
        document.querySelector('.progress-container').classList.remove('hidden');
        document.getElementById('startVideoGeneration').classList.add('hidden');
    }

    async monitorProgress() {
        const progressBar = document.querySelector('.progress');
        const statusText = document.querySelector('.status-text');
        const percentage = document.querySelector('.percentage');

        while (this.videoGenerationId) {
            try {
                const response = await fetch('/check-heygen-video', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        api_key: this.apiKey,
                        video_id: this.videoGenerationId
                    })
                });

                const data = await response.json();
                if (data.success) {
                    progressBar.style.width = `${data.progress}%`;
                    percentage.textContent = `${data.progress}%`;
                    statusText.textContent = data.status;

                    if (data.status === 'completed') {
                        this.videoGenerationId = null;
                        this.showVideo(data.video_url);
                        break;
                    } else if (data.status === 'failed') {
                        throw new Error('Video generation failed');
                    }
                } else {
                    throw new Error(data.error || 'Failed to check video status');
                }

                await new Promise(resolve => setTimeout(resolve, 2000));
            } catch (error) {
                this.showError(error.message);
                break;
            }
        }
    }

    showVideo(videoUrl) {
        const videoResult = document.querySelector('.video-result');
        const video = videoResult.querySelector('video');
        video.src = videoUrl;
        videoResult.classList.remove('hidden');
        document.querySelector('.progress-container').classList.add('hidden');
    }
}

// Initialize the manager
const heygenManager = new HeyGenManager();
