const apicalls = {
    test: function(name){
        return 'hell'
    },

    sendCoordinates: function(inputs) {
        const lat = inputs['latitude'];
        const lng = inputs['longitude'];
    
        console.log('Latitude:', lat, 'Longitude:', lng);
    
        const apiUrl = "https://rest.isric.org/soilgrids/v2.0/properties/query?lon=" + lng + "&lat=" + lat + "&property=bdod&property=cec&property=cfvo&property=clay&property=nitrogen&property=ocd&property=ocs&property=phh2o&property=sand&property=silt&property=soc&property=wv0010&property=wv0033&property=wv1500&depth=15-30cm&value=Q0.05&value=Q0.5&value=Q0.95&value=mean&value=uncertainty";
        
        return fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {

                const postData = { //combine data?
                    inputs: inputs,
                    soilData: data
                };
        
                // Send the combined data to the server
                return fetch('/save_soil_data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(postData)
                });
            })
            .then(response => response.json())
            .then(result => {
                console.log('Server response:', result);
                return result;
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

};


async function sendCoordinates(inputs) {
    const lat = inputs['latitude'];
    const lng = inputs['longitude'];
    const apiKey = '89aad8e3355c958621c3c8f2c0386aaa'
    console.log('Latitude:', lat, 'Longitude:', lng);

    try {
        // Fetch soil data
        const soilApiUrl = "https://rest.isric.org/soilgrids/v2.0/properties/query?lon=" + lng + "&lat=" + lat + "&property=bdod&property=cec&property=cfvo&property=clay&property=nitrogen&property=ocd&property=ocs&property=phh2o&property=sand&property=silt&property=soc&property=wv0010&property=wv0033&property=wv1500&depth=15-30cm&value=Q0.05&value=Q0.5&value=Q0.95&value=mean&value=uncertainty";
        const soilResponse = await fetch(soilApiUrl);
        if (!soilResponse.ok) {
            throw new Error('Soil API response was not ok');
        }
        const soilData = await soilResponse.json();

        
        const weatherBaseUrl = 'https://history.openweathermap.org/data/2.5/aggregated/year';
        const weatherUrl = `${weatherBaseUrl}?lat=${lat}&lon=${lng}&appid=${apiKey}`;
        const weatherResponse = await fetch(weatherUrl);
        if (!weatherResponse.ok) {
            throw new Error('Weather API response was not ok');
        }
        const weatherData = await weatherResponse.json();
        //const weatherData = '{123}';
    
        // Combine all data
        const postData = {
            inputs: inputs,
            soilData: soilData,
            weatherData: weatherData
        };

        // Send combined data to server
        const serverResponse = await fetch('/save_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(postData)
        });

        const result = await serverResponse.json();
        console.log('Server response:', result);
        return result;

    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// Usage:
// sendCoordinates({latitude: 123, longitude: 456}, 'your-api-key-here')
//     .then(result => console.log(result))
//     .catch(error => console.error(error));