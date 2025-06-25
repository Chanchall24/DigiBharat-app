// DigiBharat - Main JavaScript
class DigiBharatApp {
    constructor() {
        this.currentLanguage = 'en';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupFileUpload();
        this.setupLanguageToggle();
        this.showWelcomeMessage();
    }

    setupEventListeners() {
        // File input change
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            input.addEventListener('change', this.handleFileSelect.bind(this));
        });

        // Form submissions
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
        });

        // Help tooltips
        this.setupTooltips();
    }

    setupFileUpload() {
        const uploadAreas = document.querySelectorAll('.upload-area');
        
        uploadAreas.forEach(area => {
            // Drag and drop functionality
            area.addEventListener('dragover', this.handleDragOver.bind(this));
            area.addEventListener('dragleave', this.handleDragLeave.bind(this));
            area.addEventListener('drop', this.handleDrop.bind(this));
            
            // Click to upload
            area.addEventListener('click', () => {
                const fileInput = area.querySelector('input[type="file"]');
                if (fileInput) {
                    fileInput.click();
                }
            });
        });
    }

    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        e.currentTarget.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        e.currentTarget.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const uploadArea = e.currentTarget;
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const fileInput = uploadArea.querySelector('input[type="file"]');
            if (fileInput) {
                fileInput.files = files;
                this.handleFileSelect({ target: fileInput });
            }
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'application/pdf'];
        if (!allowedTypes.includes(file.type)) {
            this.showAlert('अमान्य फ़ाइल प्रकार / Invalid file type', 'error');
            return;
        }

        // Validate file size (16MB max)
        if (file.size > 16 * 1024 * 1024) {
            this.showAlert('फ़ाइल का आकार बहुत बड़ा है / File size too large', 'error');
            return;
        }

        // Show file preview
        this.showFilePreview(file, e.target);

        // Check image quality for selfies
        if (e.target.name === 'selfie') {
            this.checkImageQuality(file);
        }
    }

    showFilePreview(file, input) {
        const previewContainer = input.closest('.upload-area').querySelector('.file-preview') || 
                               this.createPreviewContainer(input.closest('.upload-area'));
        
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewContainer.innerHTML = `
                    <div class="preview-image">
                        <img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 200px; border-radius: 8px;">
                        <p class="mt-2"><strong>${file.name}</strong></p>
                        <p class="text-muted">${this.formatFileSize(file.size)}</p>
                    </div>
                `;
            };
            reader.readAsDataURL(file);
        } else {
            previewContainer.innerHTML = `
                <div class="preview-file">
                    <i class="fas fa-file-pdf fa-3x text-danger mb-2"></i>
                    <p><strong>${file.name}</strong></p>
                    <p class="text-muted">${this.formatFileSize(file.size)}</p>
                </div>
            `;
        }
    }

    createPreviewContainer(uploadArea) {
        const container = document.createElement('div');
        container.className = 'file-preview mt-3 text-center';
        uploadArea.appendChild(container);
        return container;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async checkImageQuality(file) {
        const formData = new FormData();
        formData.append('image', file);

        try {
            const response = await fetch('/api/check_image_quality', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                this.showImageQualityFeedback(result);
            }
        } catch (error) {
            console.error('Error checking image quality:', error);
        }
    }

    showImageQualityFeedback(result) {
        const { quality_score, suggestions } = result;
        
        let alertType = 'success';
        if (quality_score < 50) alertType = 'error';
        else if (quality_score < 75) alertType = 'warning';

        let message = `छवि गुणवत्ता स्कोर / Image Quality Score: ${quality_score}%`;
        
        if (suggestions.length > 0) {
            message += '\n\nसुझाव / Suggestions:\n' + suggestions.join('\n');
        }

        this.showAlert(message, alertType);
    }

    handleFormSubmit(e) {
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>प्रसंस्करण... / Processing...';
        }

        // Show loading overlay
        this.showLoading('आपके दस्तावेज़ों का सत्यापन हो रहा है... / Verifying your documents...');
    }

    showLoading(message) {
        const overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="spinner"></div>
                <p>${message}</p>
            </div>
        `;
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            color: white;
            text-align: center;
        `;
        
        document.body.appendChild(overlay);
    }

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at the top of main content
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.insertBefore(alertDiv, mainContent.firstChild);
        }

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    setupLanguageToggle() {
        const toggleBtn = document.getElementById('language-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', this.toggleLanguage.bind(this));
        }
    }

    toggleLanguage() {
        this.currentLanguage = this.currentLanguage === 'en' ? 'hi' : 'en';
        
        // Update UI elements based on language
        this.updateLanguageContent();
        
        // Store preference
        localStorage.setItem('preferred-language', this.currentLanguage);
    }

    updateLanguageContent() {
        const elements = document.querySelectorAll('[data-en][data-hi]');
        elements.forEach(el => {
            const text = el.getAttribute(`data-${this.currentLanguage}`);
            if (text) {
                el.textContent = text;
            }
        });
    }

    setupTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    showWelcomeMessage() {
        // Show welcome message for first-time users
        if (!localStorage.getItem('visited-before')) {
            setTimeout(() => {
                this.showAlert('DigiBharat में आपका स्वागत है! / Welcome to DigiBharat!', 'info');
                localStorage.setItem('visited-before', 'true');
            }, 1000);
        }
    }

    // Utility functions
    animateElement(element, animationClass) {
        element.classList.add(animationClass);
        element.addEventListener('animationend', () => {
            element.classList.remove(animationClass);
        }, { once: true });
    }

    updateProgressBar(step) {
        const steps = document.querySelectorAll('.step');
        const connectors = document.querySelectorAll('.step-connector');
        
        steps.forEach((stepEl, index) => {
            stepEl.classList.remove('active', 'completed');
            if (index + 1 < step) {
                stepEl.classList.add('completed');
            } else if (index + 1 === step) {
                stepEl.classList.add('active');
            }
        });
        
        connectors.forEach((connector, index) => {
            connector.classList.remove('completed');
            if (index + 1 < step) {
                connector.classList.add('completed');
            }
        });
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DigiBharatApp();
});

// Service Worker for offline functionality
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
