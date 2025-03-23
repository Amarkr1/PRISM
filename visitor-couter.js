// Get the current visitor count immediately when the script loads
// This runs before DOMContentLoaded to get the count as soon as possible
(function() {
    // Namespace and key for this specific site
    const namespace = 'prism-medical-imaging';
    const key = 'visitors';
    
    // First try to get the current count without incrementing
    fetch(`https://api.countapi.xyz/get/${namespace}/${key}`)
        .then(response => response.json())
        .then(data => {
            // If the counter doesn't exist yet, create it with an initial value
            if (data.value === undefined) {
                return fetch(`https://api.countapi.xyz/create?namespace=${namespace}&key=${key}&value=1`);
            }
            return data;
        })
        .then(data => {
            // Update the counter element if it exists in the DOM
            const counterElement = document.getElementById('visitor-count');
            if (counterElement) {
                counterElement.textContent = (typeof data.value === 'number') ? 
                    data.value.toLocaleString() : data.toLocaleString();
            }
        })
        .catch(error => {
            console.error('Error fetching initial visitor count:', error);
        });
})();

// Handle session-based counting after DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const namespace = 'prism-medical-imaging';
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
            });
    }
});