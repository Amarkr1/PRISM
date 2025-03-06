document.addEventListener('DOMContentLoaded', function() {
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