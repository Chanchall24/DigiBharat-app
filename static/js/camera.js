// Camera functionality for selfie capture
class CameraHandler {
    constructor() {
        this.stream = null;
        this.video = null;
        this.canvas = null;
        this.context = null;
        this.constraints = {
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user' // Front camera
            }
        };
        this.init();
    }

    init() {
        this.video = document.getElementById('camera');
        this.canvas = document.getElementById('camera-canvas');
        
        if (this.canvas) {
            this.context = this.canvas.getContext('2d');
        }

        this.setupEventListeners();
    }

    setupEventListeners() {
        // Start camera button
        const startBtn = document.getElementById('start-camera');
        if (startBtn) {
            startBtn.addEventListener('click', this.startCamera.bind(this));
        }

        // Capture button
        const captureBtn = document.getElementById('capture-btn');
        if (captureBtn) {
            captureBtn.addEventListener('click', this.capturePhoto.bind(this));
        }

        // Switch camera button
        const switchBtn = document.getElementById('switch-camera');
        if (switchBtn) {
            switchBtn.addEventListener('click', this.switchCamera.bind(this));
        }

        // Retry button
        const retryBtn = document.getElementById('retry-capture');
        if (retryBtn) {
            retryBtn.addEventListener('click', this.retryCapture.bind(this));
        }
    }

    async startCamera() {
        try {
            // Check if camera is supported
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('Camera not supported');
            }

            // Request camera permission
            this.stream = await navigator.mediaDevices.getUserMedia(this.constraints);
            
            if (this.video) {
                this.video.srcObject = this.stream;
                this.video.play();
                
                // Show camera controls
                this.showCameraControls();
                
                // Hide start button
                const startBtn = document.getElementById('start-camera');
                if (startBtn) {
                    startBtn.style.display = 'none';
                }

                // Show quality guidelines
                this.showCameraGuidelines();
            }

        } catch (error) {
            console.error('Error accessing camera:', error);
            this.handleCameraError(error);
        }
    }

    showCameraControls() {
        const controls = document.getElementById('camera-controls');
        if (controls) {
            controls.style.display = 'block';
        }
    }

    showCameraGuidelines() {
        const guidelines = document.getElementById('camera-guidelines');
        if (guidelines) {
            guidelines.innerHTML = `
                <div class="alert alert-info">
                    <h6>📸 बेहतर सेल्फी के लिए सुझाव / Tips for Better Selfie:</h6>
                    <ul class="mb-0">
                        <li>अच्छी रोशनी में फोटो लें / Take photo in good lighting</li>
                        <li>कैमरा को स्थिर रखें / Keep camera steady</li>
                        <li>चेहरा गाइड के अंदर रखें / Keep face inside the guide</li>
                        <li>सीधे कैमरे की तरफ देखें / Look directly at camera</li>
                    </ul>
                </div>
            `;
        }
    }

    capturePhoto() {
        if (!this.video || !this.canvas || !this.context) {
            this.showAlert('कैमरा तैयार नहीं है / Camera not ready', 'error');
            return;
        }

        try {
            // Set canvas dimensions
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;

            // Draw video frame to canvas
            this.context.drawImage(this.video, 0, 0);

            // Convert to blob
            this.canvas.toBlob((blob) => {
                if (blob) {
                    this.handleCapturedPhoto(blob);
                } else {
                    throw new Error('Failed to capture photo');
                }
            }, 'image/jpeg', 0.8);

        } catch (error) {
            console.error('Error capturing photo:', error);
            this.showAlert('फोटो कैप्चर करने में त्रुटि / Error capturing photo', 'error');
        }
    }

    handleCapturedPhoto(blob) {
        // Create file from blob
        const file = new File([blob], 'selfie.jpg', { type: 'image/jpeg' });
        
        // Show preview
        this.showPhotoPreview(blob);
        
        // Update file input
        const fileInput = document.getElementById('selfie-input');
        if (fileInput) {
            const dt = new DataTransfer();
            dt.items.add(file);
            fileInput.files = dt.files;
        }

        // Stop camera
        this.stopCamera();

        // Show confirmation buttons
        this.showConfirmationButtons();

        // Check image quality
        this.checkCapturedImageQuality(file);
    }

    showPhotoPreview(blob) {
        const previewContainer = document.getElementById('photo-preview');
        if (previewContainer) {
            const url = URL.createObjectURL(blob);
            previewContainer.innerHTML = `
                <div class="captured-photo">
                    <img src="${url}" alt="Captured selfie" class="img-fluid rounded">
                </div>
            `;
            previewContainer.style.display = 'block';
        }
    }

    showConfirmationButtons() {
        const confirmBtns = document.getElementById('confirmation-buttons');
        if (confirmBtns) {
            confirmBtns.innerHTML = `
                <div class="d-flex gap-3 justify-content-center">
                    <button type="button" class="btn btn-outline-primary" id="retry-capture">
                        <i class="fas fa-redo me-2"></i>फिर से लें / Retake
                    </button>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-check me-2"></i>आगे बढ़ें / Continue
                    </button>
                </div>
            `;
            confirmBtns.style.display = 'block';

            // Re-attach event listeners
            document.getElementById('retry-capture').addEventListener('click', this.retryCapture.bind(this));
        }
    }

    retryCapture() {
        // Hide preview and confirmation buttons
        const previewContainer = document.getElementById('photo-preview');
        const confirmBtns = document.getElementById('confirmation-buttons');
        
        if (previewContainer) previewContainer.style.display = 'none';
        if (confirmBtns) confirmBtns.style.display = 'none';

        // Clear file input
        const fileInput = document.getElementById('selfie-input');
        if (fileInput) {
            fileInput.value = '';
        }

        // Restart camera
        this.startCamera();
    }

    switchCamera() {
        // Toggle between front and back camera
        const currentFacingMode = this.constraints.video.facingMode;
        this.constraints.video.facingMode = currentFacingMode === 'user' ? 'environment' : 'user';
        
        // Restart camera with new constraints
        this.stopCamera();
        this.startCamera();
    }

    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }

        if (this.video) {
            this.video.srcObject = null;
        }
    }

    handleCameraError(error) {
        let message = 'कैमरा एक्सेस करने में त्रुटि / Error accessing camera';
        
        if (error.name === 'NotAllowedError') {
            message = 'कैमरा की अनुमति दें / Please allow camera access';
        } else if (error.name === 'NotFoundError') {
            message = 'कैमरा नहीं मिला / Camera not found';
        } else if (error.name === 'NotSupportedError') {
            message = 'कैमरा समर्थित नहीं है / Camera not supported';
        }

        this.showAlert(message, 'error');

        // Show file upload option as fallback
        this.showFileUploadFallback();
    }

    showFileUploadFallback() {
        const fallback = document.getElementById('file-upload-fallback');
        if (fallback) {
            fallback.innerHTML = `
                <div class="alert alert-warning">
                    <h6>📱 वैकल्पिक तरीका / Alternative Method:</h6>
                    <p>कैमरा उपलब्ध नहीं है। कृपया अपनी गैलरी से सेल्फी अपलोड करें।</p>
                    <p>Camera not available. Please upload selfie from your gallery.</p>
                </div>
            `;
            fallback.style.display = 'block';
        }
    }

    async checkCapturedImageQuality(file) {
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
        const feedbackContainer = document.getElementById('quality-feedback');
        
        if (feedbackContainer) {
            let alertClass = 'alert-success';
            let icon = '✅';
            
            if (quality_score < 50) {
                alertClass = 'alert-danger';
                icon = '❌';
            } else if (quality_score < 75) {
                alertClass = 'alert-warning';
                icon = '⚠️';
            }

            feedbackContainer.innerHTML = `
                <div class="alert ${alertClass}">
                    <h6>${icon} छवि गुणवत्ता स्कोर / Image Quality Score: ${quality_score}%</h6>
                    ${suggestions.length > 0 ? `
                        <ul class="mb-0 mt-2">
                            ${suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                        </ul>
                    ` : ''}
                </div>
            `;
        }
    }

    showAlert(message, type = 'info') {
        // Use the main app's alert system
        if (window.digiBharatApp && window.digiBharatApp.showAlert) {
            window.digiBharatApp.showAlert(message, type);
        } else {
            alert(message);
        }
    }

    // Cleanup when page is unloaded
    cleanup() {
        this.stopCamera();
    }
}

// Initialize camera handler when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.cameraHandler = new CameraHandler();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.cameraHandler) {
        window.cameraHandler.cleanup();
    }
});
