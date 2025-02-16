// export function sendCoordinates(lat, lng) {
//     console.log('Latitude:', lat, 'Longitude:', lng);
//     const apiUrl = "https://rest.isric.org/soilgrids/v2.0/properties/query?lon=" + lng + "&lat=" + lat + "&property=bdod&property=cec&property=cfvo&property=clay&property=nitrogen&property=ocd&property=ocs&property=phh2o&property=sand&property=silt&property=soc&property=wv0010&property=wv0033&property=wv1500&depth=15-30cm&value=Q0.05&value=Q0.5&value=Q0.95&value=mean&value=uncertainty";

//     fetch(apiUrl)
//         .then(response => {
//             if (!response.ok) {
//                 throw new Error('Network response was not ok');
//             }
//             return response.json();
//         })
//         .then(data => {
//             // Send the data to the server
//             return fetch('/save_soil_data', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                 },
//                 body: JSON.stringify(data)
//             });
//         })
//         .then(response => response.json())
//         .then(result => {
//             console.log('Server response:', result);
//         })
//         .catch(error => {
//             console.error('Error:', error);
//         });
//     }

const apicalls = {
    test: function(name){
        return 'hell'
    },

    sendCoordinates: function(lat, lng) {
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
                    // Send the data to the server
                    return fetch('/save_soil_data', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
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