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
    
    // First check if this counter exists, if not create it
    fetch(`https://api.countapi.xyz/get/${namespace}/${key}`)
        .then(response => response.json())
        .then(data => {
            // If counter doesn't exist or returned an error
            if (!data.value) {
                // Create a new counter starting at 42
                return fetch(`https://api.countapi.xyz/set/${namespace}/${key}?value=42`)
                    .then(response => response.json());
            }
            return data;
        })
        .then(data => {
            // Always increment the counter on page visit (no session check)
            return fetch(`https://api.countapi.xyz/hit/${namespace}/${key}`)
                .then(response => response.json());
        })
        .then(data => {
            // Update the display with the new value
            updateVisitorCount(data.value);
        })
        .catch(error => {
            console.error('Error with visitor counter:', error);
            // Keep the default value from HTML in case of error
        });
});