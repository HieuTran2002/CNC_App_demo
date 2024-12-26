function triggerEvent(msg) {
    fetch('/trigger_button', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            timestamp: new Date().toISOString(),
            message: msg,
        })
    })
    .then(response => response.json())
    .then(data => {
         
         console.log(`Event triggered successfully at ${new Date().toLocaleTimeString()}`);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// List of img elements' IDs to monitor
const imgElements = [
    'result1',
];

// Function to check if the image has been updated and refresh the src attribute
function checkForImageUpdates() {
    imgElements.forEach(elementId => {
        fetch(`/get_image_path/${elementId}`)
            .then(response => response.json())
            .then(data => {
                if (data.image_path) {
                    const imgElement = document.getElementById(elementId);
                    if (imgElement) {
                        imgElement.src = data.image_path; // Update the img src with the new image path
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching image path:', error);
            });
    });
}

// Set an interval to check for updates every 1 seconds (or adjust as needed)
setInterval(checkForImageUpdates, 1000);
