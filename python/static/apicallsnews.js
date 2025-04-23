const apicalls = {
    sendCoordinates: function(inputs) {
        return fetch('/api/get-soil-weather', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(inputs),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch data from backend');
            }
            return response.json();
        })
        .then(result => {
            console.log('Server response:', result);
            return result;
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
};
