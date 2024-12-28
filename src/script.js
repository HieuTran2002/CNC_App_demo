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

