// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get the counter element
    const counterElement = document.getElementById('visitor-count');
    
    // Check if we've already counted this visitor in this session
    const sessionKey = 'prism-visitor-counted';
    const hasBeenCounted = sessionStorage.getItem(sessionKey);
    
    // Cloudflare Worker URL - our deployed worker
    const workerBaseUrl = 'https://prism.amar-kumar.workers.dev';
    
    // Function to update the display with count
    function updateCounterDisplay(count) {
        if (counterElement) {
            counterElement.textContent = count.toLocaleString();
        }
    }
    
    // Function to handle errors
    function handleError(error) {
        console.error('Error with visitor counter:', error);
        // If error occurs, show a default value
        if (counterElement) {
            counterElement.textContent = '42+';
        }
    }
    
    try {
        if (!hasBeenCounted) {
            // New session - increment the counter
            fetch(`${workerBaseUrl}/increment`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    updateCounterDisplay(data.count);
                    // Mark this session as counted
                    sessionStorage.setItem(sessionKey, 'true');
                })
                .catch(handleError);
        } else {
            // Returning visitor in same session - just get current count
            fetch(`${workerBaseUrl}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    updateCounterDisplay(data.count);
                })
                .catch(handleError);
        }
    } catch (error) {
        handleError(error);
    }
});