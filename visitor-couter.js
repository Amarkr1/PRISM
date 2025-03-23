// Visitor counter script
document.addEventListener('DOMContentLoaded', function() {
    // Use CountAPI as a simple, no-setup backend for counting
    const namespace = 'prism-medical-imaging'; // Choose a unique namespace for your site
    const key = 'visitors';
    
    // Function to update the counter display
    function updateVisitorCount(count) {
        const counterElement = document.getElementById('visitor-count');
        if (counterElement) {
            counterElement.textContent = count.toLocaleString();
        }
    }
    
    // Check if this is a new session
    const lastVisit = sessionStorage.getItem('lastVisit');
    const currentTime = new Date().getTime();
    
    if (!lastVisit || (currentTime - parseInt(lastVisit)) > 1000 * 60 * 30) { // 30 minute session
        // This is a new session, increment the counter
        fetch(`https://api.countapi.xyz/hit/${namespace}/${key}`)
            .then(response => response.json())
            .then(data => {
                updateVisitorCount(data.value);
                // Save the visit time
                sessionStorage.setItem('lastVisit', currentTime.toString());
            })
            .catch(error => {
                console.error('Error updating visitor count:', error);
                // Fallback: just get the current count
                fetch(`https://api.countapi.xyz/get/${namespace}/${key}`)
                    .then(response => response.json())
                    .then(data => {
                        updateVisitorCount(data.value);
                    })
                    .catch(e => console.error('Failed to get visitor count:', e));
            });
    } else {
        // This is a returning visitor within the same session, just get the current count
        fetch(`https://api.countapi.xyz/get/${namespace}/${key}`)
            .then(response => response.json())
            .then(data => {
                updateVisitorCount(data.value);
            })
            .catch(error => {
                console.error('Error fetching visitor count:', error);
            });
    }
});