document.addEventListener('DOMContentLoaded', function() {
    // Visitor counter functionality - tracking unique visitors
    function updateVisitorCount() {
        const visitorCountElement = document.getElementById('visitor-count');
        if (!visitorCountElement) {
            console.error("Visitor count element not found!");
            return;
        }
        
        // Check if this is a new visitor using sessionStorage
        const hasVisitedThisSession = sessionStorage.getItem('hasVisitedThisSession');
        
        // If this is a deployment preview or local development, 
        // use a simulated count that looks realistic
        if (window.location.hostname === 'localhost' || 
            window.location.hostname.includes('preview') || 
            window.location.hostname.includes('staging')) {
            
            // For testing: Generate a random visitor count
            const baseCount = 1275;  // Start with a realistic number
            const randomIncrement = Math.floor(Math.random() * 50) + 1;
            visitorCountElement.textContent = (baseCount + randomIncrement).toLocaleString();
            
            if (!hasVisitedThisSession) {
                sessionStorage.setItem('hasVisitedThisSession', 'true');
                console.log("Visit recorded (preview mode)");
            }
            
            return;
        }
        
        // For production website: Try to use the server API
        try {
            if (!hasVisitedThisSession) {
                // This is a new session, record the visit
                fetch('/api/visitors/record', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        visitorCountElement.textContent = data.count.toLocaleString();
                        sessionStorage.setItem('hasVisitedThisSession', 'true');
                    }
                })
                .catch(error => {
                    console.error("Error recording visit:", error);
                    fallbackVisitorCount(visitorCountElement);
                });
            } else {
                // Just fetch the current count
                fetch('/api/visitors/count')
                    .then(response => response.json())
                    .then(data => {
                        visitorCountElement.textContent = data.count.toLocaleString();
                    })
                    .catch(error => {
                        console.error("Error fetching visitor count:", error);
                        fallbackVisitorCount(visitorCountElement);
                    });
            }
        } catch (error) {
            console.error("Visitor counter error:", error);
            fallbackVisitorCount(visitorCountElement);
        }
    }
    
    // Fallback method if the API calls fail
    function fallbackVisitorCount(element) {
        // Use localStorage as a fallback
        let count = localStorage.getItem('visitorCount');
        if (!count) {
            count = 0;  // Start with a plausible number
            localStorage.setItem('visitorCount', count);
        }
        element.textContent = Number(count).toLocaleString();
    }
    
    // Initialize visitor counter
    updateVisitorCount();
    
    // Gallery scrolling functionality
    const gallery = document.getElementById('image-gallery');
    const scrollLeftBtn = document.getElementById('scroll-left');
    const scrollRightBtn = document.getElementById('scroll-right');
    
    // Scroll amount for each button click
    const scrollAmount = 330; // Slightly more than image width to account for gap
    
    if (scrollLeftBtn && scrollRightBtn && gallery) {
        scrollLeftBtn.addEventListener('click', function() {
            gallery.scrollBy({
                left: scrollAmount,
                behavior: 'smooth'
            });
        });
        
        scrollRightBtn.addEventListener('click', function() {
            gallery.scrollBy({
                left: -scrollAmount,
                behavior: 'smooth'
            });
        });
    }
    
    // GIF toggle functionality
    const toggleButtons = document.querySelectorAll('.toggle-play-btn');
    
    // Create a single transparent 1x1 pixel image to use for pausing
    const transparentPixel = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
    
    toggleButtons.forEach(button => {
        // Get the related GIF image
        const gifItem = button.closest('.gif-item');
        const gifImage = gifItem.querySelector('.gif-image');
        
        // Store original source on first load
        if (!gifImage.hasAttribute('data-original-src')) {
            gifImage.setAttribute('data-original-src', gifImage.src);
        }
        
        button.addEventListener('click', function() {
            const isPlaying = this.getAttribute('data-status') === 'playing';
            
            if (isPlaying) {
                // PAUSE: Store current source if needed
                if (!gifImage.hasAttribute('data-original-src')) {
                    gifImage.setAttribute('data-original-src', gifImage.src);
                }
                
                // Replace with transparent pixel to stop animation
                gifImage.src = transparentPixel;
                
                // Update button state
                this.setAttribute('data-status', 'paused');
                this.innerHTML = '<i class="fas fa-play"></i> Play Animation';
            } else {
                // PLAY: Restore original GIF with timestamp to force reload
                const originalSrc = gifImage.getAttribute('data-original-src');
                if (originalSrc) {
                    gifImage.src = originalSrc + '?t=' + Date.now();
                }
                
                // Update button state
                this.setAttribute('data-status', 'playing');
                this.innerHTML = '<i class="fas fa-pause"></i> Pause Animation';
            }
        });
    });
    
    // Feedback form functionality (Formspree integration)
    const feedbackIcon = document.getElementById('feedbackIcon');
    const feedbackModal = document.getElementById('feedbackModal');
    const closeBtn = document.querySelector('.close-feedback');
    
    // If feedback elements exist, set up event listeners
    if (feedbackIcon && feedbackModal) {
        // Open modal when clicking the feedback icon
        feedbackIcon.addEventListener('click', function() {
            feedbackModal.style.display = 'flex';
        });
        
        // Close modal when clicking the X button
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                feedbackModal.style.display = 'none';
            });
        }
        
        // Close modal when clicking outside the content
        window.addEventListener('click', function(event) {
            if (event.target === feedbackModal) {
                feedbackModal.style.display = 'none';
            }
        });
        
        // Handle form submission to reset fields
        const feedbackForm = document.getElementById('feedbackForm');
        if (feedbackForm) {
            feedbackForm.addEventListener('submit', function() {
                // Set a small timeout to allow the form to submit before resetting
                setTimeout(() => {
                    // Reset the form fields
                    this.reset();
                }, 100);
            });
        }
    }
});