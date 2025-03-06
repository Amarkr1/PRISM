document.addEventListener('DOMContentLoaded', function() {
    // Visitor counter functionality for website deployment
    function updateVisitorCount() {
        const visitorCountElement = document.getElementById('visitor-count');
        if (!visitorCountElement) return;
        
        // For demonstration: Start with a base count and increment based on timestamp
        // This simulates a growing visitor count in a demo environment
        const baseCount = 1275; // Starting with a realistic number
        
        // Options for a real implementation:
        
        // OPTION 1: Fetch from server API
        // This would be the proper approach for a real website
        /*
        fetch('/api/visitors/count')
            .then(response => response.json())
            .then(data => {
                visitorCountElement.textContent = data.count;
            })
            .catch(error => {
                console.error('Error fetching visitor count:', error);
                visitorCountElement.textContent = baseCount;
            });
        */
        
        // OPTION 2: Use a third-party analytics service
        // Many sites use Google Analytics, Plausible, or similar services
        // These typically provide their own tracking code
        
        // For now, using a simulated count for demonstration
        const randomIncrement = Math.floor(Math.random() * 50) + 1;
        const simulatedCount = baseCount + randomIncrement;
        visitorCountElement.textContent = simulatedCount.toLocaleString();
        
        // Record visit (in a real implementation, this would call your analytics service)
        const hasVisitedThisSession = sessionStorage.getItem('hasVisitedThisSession');
        if (!hasVisitedThisSession) {
            sessionStorage.setItem('hasVisitedThisSession', 'true');
            // In a real implementation, this would be where you'd call your API:
            // fetch('/api/visitors/record', {method: 'POST'});
        }
    }
    
    // Call the visitor counter update function
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
});