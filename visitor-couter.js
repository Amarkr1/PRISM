// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get the counter element
    const counterElement = document.getElementById('visitor-count');
    
    // Use CountAPI as a backend for counting
    const namespace = 'prism-medical-imaging'; // Unique namespace for your site
    const key = 'visitors';
    
    // Function to update the counter display
    function updateVisitorCount(count) {
        if (counterElement) {
            counterElement.textContent = count.toLocaleString();
        }
    }
    
    // Function to handle errors
    function handleError(error) {
        console.error('Error with visitor counter:', error);
        // Keep the default value from HTML in case of error
    }
    
    // Check if counter exists, create it if not, then increment
    fetch(`https://api.countapi.xyz/get/${namespace}/${key}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // If counter doesn't exist or returned an error
            if (data.value === undefined || data.value === null) {
                // Create a new counter starting at 42
                return fetch(`https://api.countapi.xyz/set/${namespace}/${key}?value=42`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Failed to set counter');
                        }
                        return response.json();
                    });
            }
            return data;
        })
        .then(data => {
            // First display current value
            updateVisitorCount(data.value);
            
            // Then increment the counter on page visit
            return fetch(`https://api.countapi.xyz/hit/${namespace}/${key}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to increment counter');
                    }
                    return response.json();
                });
        })
        .then(data => {
            // Update the display with the new incremented value
            updateVisitorCount(data.value);
        })
        .catch(handleError);
});