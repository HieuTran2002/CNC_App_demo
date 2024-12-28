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
