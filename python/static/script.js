mapboxgl.accessToken = 'pk.eyJ1Ijoia2F0Y3Jhd2ZvcmQiLCJhIjoiY203NXJ0ZTR6MDB3MzJucHo2ZmppNmR1YSJ9.KKea34jSVKuLRBfYQhSfJw';

const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/satellite-streets-v12',
    center: [-100, 42.76],
    zoom: 3
});

document.querySelectorAll('input[name="mode-toggle"]').forEach(el => {
    el.addEventListener('change', function () {
        const advancedOptions = document.getElementById('advanced-options');
        if (document.getElementById('advanced-mode').checked) {
            advancedOptions.style.display = 'block';
        } else {
            advancedOptions.style.display = 'none';
        }
    });
});

// Constants
const EARTH_RADIUS_KM = 6367;
const MILES_PER_KM = 0.621371;
const TOP_N = 3; // Choose how many top entries you want

// Helper function to convert degrees to radians
function toRadians(degrees) {
    return degrees * Math.PI / 180;
}

// Function to calculate the distance between two points using the Haversine formula
function getDistance(lon1, lat1, lon2, lat2) {
    lon1 = toRadians(lon1);
    lat1 = toRadians(lat1);
    lon2 = toRadians(lon2);
    lat2 = toRadians(lat2);

    const dlon = lon2 - lon1;
    const dlat = lat2 - lat1;

    const a = Math.sin(dlat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dlon / 2) ** 2;
    const c = 2 * Math.asin(Math.sqrt(a));

    const distanceKm = EARTH_RADIUS_KM * c;
    const distanceMiles = distanceKm * MILES_PER_KM;

    return distanceMiles;
}

// Fetch and parse CSV data from the URLs
async function fetchAndParseCSV(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Failed to fetch CSV data from ${url}`);
    }
    const csvText = await response.text();
    return parseCSV(csvText);
}

function parseCSV(csvText) {
    const [headerLine, ...lines] = csvText.split('\n');
    const headers = headerLine.split(',');

    const validRows = lines.filter(line => !isNaN(line.charAt(0)));

    return validRows.map(line => {
        const values = line.split(',');
        return {
            Latitude: values[12],
            Longitude: values[13]
        };
    });
}

// Fetch and compile top N longitudes and latitudes
async function fetchTopLocations(latitude, longitude, commodity, topN) {
    const locations = [
        [-90, -180], [-61.085498574354446, -180], [-61.085498574354446, -128.57142857142856],
        [-61.085498574354446, -77.14285714285712], [-61.085498574354446, -25.714285714285694],
        [-61.085498574354446, 25.714285714285737], [-61.085498574354446, 77.14285714285717],
        [-61.085498574354446, 128.5714285714286], [-32.17099714870889, -180],
        [-32.17099714870889, -147.27272727272728], [-32.17099714870889, -114.54545454545456],
        [-32.17099714870889, -81.81818181818184], [-32.17099714870889, -49.090909090909115],
        [-32.17099714870889, -16.363636363636388], [-32.17099714870889, 16.36363636363634],
        [-32.17099714870889, 49.090909090909065], [-32.17099714870889, 81.81818181818178],
        [-32.17099714870889, 114.5454545454545], [-32.17099714870889, 147.27272727272722],
        [-32.17099714870889, 179.99999999999994], [-3.2564957230633382, -180],
        [-3.2564957230633382, -152.30769230769232], [-3.2564957230633382, -124.61538461538463],
        [-3.2564957230633382, -96.92307692307693], [-3.2564957230633382, -69.23076923076924],
        [-3.2564957230633382, -41.53846153846155], [-3.2564957230633382, -13.846153846153854],
        [-3.2564957230633382, 13.84615384615384], [-3.2564957230633382, 41.53846153846153],
        [-3.2564957230633382, 69.23076923076923], [-3.2564957230633382, 96.92307692307692],
        [-3.2564957230633382, 124.61538461538461], [-3.2564957230633382, 152.30769230769232],
        [25.658005702582216, -180], [25.658005702582216, -150.0], [25.658005702582216, -120.0],
        [25.658005702582216, -90.0], [25.658005702582216, -60.0], [25.658005702582216, -30.0],
        [25.658005702582216, 0.0], [25.658005702582216, 30.0], [25.658005702582216, 60.0],
        [25.658005702582216, 90.0], [25.658005702582216, 120.0], [25.658005702582216, 150.0],
        [54.57250712822777, -180], [54.57250712822777, -135.0], [54.57250712822777, -90.0],
        [54.57250712822777, -45.0], [54.57250712822777, 0.0], [54.57250712822777, 45.0],
        [54.57250712822777, 90.0], [54.57250712822777, 135.0], [83.48700855387332, -180],
        [83.48700855387332, 0.0]
    ];

    // Function to find locations within 1000 miles
    function locationsWithin1000Miles(locations, lat, lon) {
        const nearbyLocations = [];
        locations.forEach(location => {
            const distance = getDistance(lon, lat, location[1], location[0]);
            if (distance <= 1000) {
                nearbyLocations.push(location);
            }
        });
        return nearbyLocations;
    }

    // Get nearby locations within 1000 miles
    const nearbyLocations = locationsWithin1000Miles(locations, latitude, longitude);

    // Generate filenames
    const files = nearbyLocations.map(location =>
        `https://raw.githubusercontent.com/K-Crawford/national-mine-repo/refs/heads/main/${commodity}%3A${location[0]}%3A${location[1]}.csv`
    );

    // Fetch and compile top N longitudes and latitudes
    async function fetchTopNLongLat(topN) {
        const promises = files.map(fetchAndParseCSV);
        const allCSVData = await Promise.all(promises);
        let allLocations = [];

        allCSVData.forEach(data => {
            data.forEach(record => {
                if (record.Latitude && record.Longitude) {
                    allLocations.push({ latitude: parseFloat(record.Latitude), longitude: parseFloat(record.Longitude) });
                }
            });
        });

        allLocations.sort((a, b) => b.latitude - a.latitude); // Example sort: by latitude in descending order

        return allLocations.slice(0, topN);
    }

    return fetchTopNLongLat(topN);
}

// map.on('load', () => {
//     document.getElementById('map-toggle').addEventListener('change', function () {
//         if (this.checked) {
//             console.log('Toggle is ON');

//             var featureCollection = []; // Initialize empty collection

//             // Your longLat collection
//             var longLat = fetchTopLocations(centerPoint[1], centerPoint[0], document.getElementById("dropdown1").value, 3)

//             // for every item object within longLat
//             for(var itemIndex in longLat) {
//             // push new feature to the collection
//                 featureCollection.push({
//                     "type": "Feature",
//                     "geometry": {
//                     "type": "Point",
//                     "coordinates": longLat[itemIndex]
//                     },
//                     "properties": {
//                     "title": "Mapbox DC",
//                     "icon": "monument"
//                     }
//                 });
//             }

//             map.on('load', function () {
//                 map.addLayer({
//                   "id": "points",
//                   "type": "symbol",
//                   "source": {
//                   "type": "geojson",
//                     "data": {
//                       "type": "FeatureCollection",
//                       "features": featureCollection 
//                     }
//                   },
//                   "layout": {
//                     "icon-image": "{icon}-15",
//                     "text-field": "{title}",
//                     "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
//                     "text-offset": [0, 0.6],
//                     "text-anchor": "top"
//                   }
//                 });
//             });
//         } else {
//             console.log('Toggle is OFF');
//             if (map.getLayer('points')) {
//                 map.removeLayer('points');
//             }
//         }
//     });
// });

// map.on('load', () => {
//     document.getElementById('map-toggle').addEventListener('change', function () {
//         if (this.checked) {
//             console.log('Toggle is ON');
//             if (!map.getSource('earthquakes')) {
//                 map.addSource('earthquakes', {
//                     type: 'geojson',
//                     data: 'https://docs.mapbox.com/mapbox-gl-js/assets/earthquakes.geojson'
//                 });
//             }
//             if (!map.getLayer('earthquakes-layer')) {
//                 map.addLayer({
//                     'id': 'earthquakes-layer',
//                     'type': 'circle',
//                     'source': 'earthquakes',
//                     'paint': {
//                         'circle-radius': 4,
//                         'circle-stroke-width': 2,
//                         'circle-color': 'green',
//                         'circle-stroke-color': 'white'
//                     }
//                 });
//             }
//         } else {
//             console.log('Toggle is OFF');
//             if (map.getLayer('earthquakes-layer')) {
//                 map.removeLayer('earthquakes-layer');
//             }
//             if (map.getSource('earthquakes')) {
//                 map.removeSource('earthquakes');
//             }
//         }
//     });
// });

map.on('load', () => {
    document.getElementById('map-toggle').addEventListener('change', function () {
        if (this.checked) {
            console.log('Toggle is ON');
            if (!map.getSource('mines')) {
                map.addSource('mines', {
                    type: 'geojson',
                    data: "https://raw.githubusercontent.com/K-Crawford/mines/main/DMR_All_Mines.geojson"
                });
            }
            if (!map.getLayer('mines-layer')) {
                map.addLayer({
                    'id': 'mines-layer',
                    'type': 'circle',
                    'source': 'mines',
                    'paint': {
                        'circle-radius': 5,
                        'circle-stroke-width': 1,
                        'circle-color': 'green',
                        'circle-stroke-color': 'white'
                    }
                });
            }
        } else {
            console.log('Toggle is OFF');
            if (map.getLayer('mines-layer')) {
                map.removeLayer('mines-layer');
            }
            if (map.getSource('mines')) {
                map.removeSource('mines');
            }
        }
    });
});

const layerList = document.getElementById('menu');
const inputs = layerList.getElementsByTagName('input');
map.getCanvas().style.cursor = 'crosshair';

for (const input of inputs) {
    input.onclick = (layer) => {
        const layerId = layer.target.id;
        map.setStyle('mapbox://styles/mapbox/' + layerId);
    };
}

window.addEventListener('load', () => {
    const searchBox = new MapboxSearchBox();
    searchBox.accessToken = mapboxgl.accessToken;
    searchBox.options = {
        types: 'address,poi',
        proximity: [-73.99209, 40.68933]
    };
    searchBox.marker = true;
    searchBox.mapboxgl = mapboxgl;
    map.addControl(searchBox);
    map.addControl(new mapboxgl.NavigationControl());
});

let centerPoint = null;
let radiusCircle = null;
let isDragging = false;
let select_clicks = 0;

function createRadiusCircle(radius) {
    const options = { steps: 64, units: 'kilometers' };
    return turf.circle(centerPoint, radius, options);
}

map.on('click', (e) => {
    if(select_clicks == 2){
        select_clicks = 0;
        if (map.getLayer('circle')) {
            map.removeLayer('circle');
            map.removeSource('circle');
        }
        map.getCanvas().style.cursor = 'crosshair';
        return;
    }

    if (select_clicks == 1) {
        select_clicks = 2;
        map.off('mousemove', updateCircle);
        map.getCanvas().style.cursor = 'pointer';
        return;
    }

    centerPoint = [e.lngLat.lng, e.lngLat.lat];
    radiusCircle = createRadiusCircle(0);

    if (map.getLayer('circle')) {
        map.getSource('circle').setData(radiusCircle);
    } else {
        map.addLayer({
            id: 'circle',
            type: 'fill',
            source: {
                type: 'geojson',
                data: radiusCircle
            },
            paint: {
                'fill-color': '#588157',
                'fill-opacity': 0.5
            }
        });
    }
    select_clicks = 1;
    map.on('mousemove', updateCircle);
    map.getCanvas().style.cursor = 'ew-resize';
});

function updateCircle(e) {
    if (select_clicks != 1) return;
    const newPoint = turf.point([e.lngLat.lng, e.lngLat.lat]);
    const from = turf.point(centerPoint);
    const distance = turf.distance(from, newPoint, { units: 'kilometers' });

    radiusCircle = createRadiusCircle(distance);
    map.getSource('circle').setData(radiusCircle);

    const info = document.getElementById('circle-info');
    info.innerHTML = `<p><strong>Radius:</strong> ${distance.toFixed(2)} km</p><p><strong>Center:</strong> [${centerPoint[0].toFixed(6)}, ${centerPoint[1].toFixed(6)}]</p>`;
}


let prog_int_bar;
let factInterval;
let modalOverlay;
let loaded = false;
let currentProgress = 0;

function updateProgressBar(progressBarFill, value) {
    progressBarFill.style.width = value + '%';
}

function loadingScreen() {
    const rockInfo = {
        basalt: {
            fact: "A volcanic rock widely used in ERW due to its availability and effectiveness in capturing carbon dioxide. It can sequester up to 2 tons of CO2 per hectare per year.",
            image: "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi5Ab9-k1VTTwU6c01anYvkaZjjXPiAfSaOSG7JOOtHk1OOr2-sT8Dz0hizGu5aj11Og7Y6YfQFTysFH72AMCCAguyz16eTbrMjqLaXQA_2YsCSrCGnTRhr_-ADuem3xs-KYwatK5BEgaM/s1600/00304+IMG_6190+8+cm+basalt+Giant%27s+Causeway.jpg"
        },
        olivine: {
            fact: "A magnesium and iron-rich rock that weathers quickly, providing fast carbon sequestration. It can capture up to 5 tons of CO2 per hectare per year.",
            image: "https://www.eiscolabs.com/cdn/shop/products/zithhqaxxcw8nqruqm5g_97322a9d-2e6d-47ee-a8df-3572db08a018_768x700.jpg?v=1578950084"
        },
        serpentinite: {
            fact: "A magnesium-rich rock high in nickel, capable of capturing up to 0.5 tons of CO2 per hectare per year.",
            image: "https://live.staticflickr.com/8684/16755884589_064a026ccf_c.jpg"
        },
        wollastonite: {
            fact: "A calcium silicate mineral found in skarns, which has potential for CO2 sequestration.",
            image: "https://www.nordkalk.com/wp-content/uploads/2022/04/Wollastonite_Nordkalk.png"
        },
        glauconite: {
            fact: "Also known as greensand, this iron potassium phyllosilicate has known plant nutritional properties and is effective in capturing carbon.",
            image: "https://www.alexstrekeisen.it/immagini/diagrammi/glauconite34803(2).jpg"
        },
        kimberlite: {
            fact: "A mineralogically complex feedstock with vast capacities to sequester carbon dioxide.",
            image: "https://www.mindat.org/imagecache/1b/05/01636270017271952473902.jpg"
        },
        brucite: {
            fact: "A magnesium hydroxide mineral that can be used as a feedstock for ERW.",
            image: "https://upload.wikimedia.org/wikipedia/commons/7/79/Brucite-231242.jpg"
        },
        feldspar: {
            fact: "A group of rock-forming tectosilicate minerals that can release potassium during weathering.",
            image: "https://mineralseducationcoalition.org/wp-content/uploads/Feldspar2_353331161.jpg"
        },
        apatite: {
            fact: "A phosphate mineral that can release phosphorus during weathering, potentially reducing the need for chemical fertilizers.",
            image: "https://crystaldreamsworld.com/wp-content/uploads/2022/10/APF-001-Blue-Apatite-Polished-Free-form-5.jpg"
        }
    };

    let currentFactIndex = 0;
    let totalProgress = 100;
    // let progressInterval;
    // let factInterval;

    modalOverlay = document.createElement('div');
    modalOverlay.id = 'modal-overlay';
    modalOverlay.className = 'modal-overlay';

    const modalContent = document.createElement('div');
    modalContent.className = 'modal-content';
    
    const progressLabel = document.createElement('div');
    progressLabel.className = 'progress-label';
    progressLabel.textContent = 'Crunching Data...';
    
    const progressBar = document.createElement('div');
    progressBar.className = 'progress-bar';
    
    const progressBarFill = document.createElement('span');
    progressBarFill.className = 'progress-bar-fill';
    progressBarFill.id = 'prog-bar';

    progressBar.appendChild(progressBarFill);
    
    const contentWrapper = document.createElement('div');
    contentWrapper.className = 'content-wrapper';
    
    const imageContainer = document.createElement('div');
    imageContainer.className = 'image-container';
    
    const rockImage = document.createElement('img');
    rockImage.id = 'rock-image';
    rockImage.alt = 'Rock Image';
    
    imageContainer.appendChild(rockImage);

    const textContainer = document.createElement('div');
    textContainer.className = 'text-container';

    const rockTitle = document.createElement('p');
    rockTitle.id = 'rock-title';
    rockTitle.className = 'rock-title';

    const modalMessage = document.createElement('p');
    modalMessage.id = 'modal-message';
    modalMessage.className = 'modal-message';

    textContainer.appendChild(rockTitle);
    textContainer.appendChild(modalMessage);

    contentWrapper.appendChild(imageContainer);
    contentWrapper.appendChild(textContainer);

    modalContent.appendChild(progressLabel);
    modalContent.appendChild(progressBar);
    modalContent.appendChild(contentWrapper);

    modalOverlay.appendChild(modalContent);

    document.body.appendChild(modalOverlay);

    

    function rotateFunFacts(funFacts, rockTitle, modalMessage, imageElement, currentIndex) {
        const rockKeys = Object.keys(funFacts);
        const currentRockKey = rockKeys[currentIndex];
        const currentRock = funFacts[currentRockKey];
        rockTitle.innerText = currentRockKey.charAt(0).toUpperCase() + currentRockKey.slice(1);
        modalMessage.innerText = currentRock.fact;
        imageElement.src = currentRock.image;
        return (currentIndex + 1) % rockKeys.length;
    }

    function progressBar1(rockInfo, progressIntervalTime = 2000, factIntervalTime = 5000) {
        console.log('');
        modalOverlay.style.display = 'flex';

        currentFactIndex = rotateFunFacts(rockInfo, rockTitle, modalMessage, rockImage, currentFactIndex);

        // let currentProgress = 0;

        prog_int_bar = setInterval(() => {
            if (currentProgress >= totalProgress) {
                clearInterval(prog_int_bar);
                clearInterval(factInterval);
                modalOverlay.style.display = 'none';
                document.body.removeChild(modalOverlay);
            } else {
                currentProgress += 5;
                updateProgressBar(progressBarFill, currentProgress);
            }
        }, progressIntervalTime / totalProgress * 100);

        factInterval = setInterval(() => {
            currentFactIndex = rotateFunFacts(rockInfo, rockTitle, modalMessage, rockImage, currentFactIndex);
        }, factIntervalTime);
    }

    progressBar1(rockInfo);

    // Styles for modal (normally you would have them in a CSS file or inside <style> tags)
    const style = document.createElement('style');
    style.innerHTML = `
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }
        .modal-content {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            width: 80%;
            max-width: 800px;
            height: 400px;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            font-family: 'Roboto Slab', serif;
        }
        .progress-label {
            margin-bottom: 10px;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Roboto Slab', serif;
        }
        .progress-bar {
            width: 100%;
            background-color: #DAD7CD;
            padding: 3px;
            border-radius: 3px;
            box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
            margin-bottom: 20px;
            font-family: 'Roboto Slab', serif;
        }
        .progress-bar-fill {
            display: block;
            height: 22px;
            background-color: #588157;
            border-radius: 3px;
            width: 0%;
            transition: width 500ms ease-in-out;
            font-family: 'Roboto Slab', serif;
        }
        .content-wrapper {
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 100%;
            font-family: 'Roboto Slab', serif;
        }
        .text-container {
            flex: 1;
            padding-left: 20px;
            text-align: left;
            overflow-y: auto;
            margin-right: 50px;
            font-family: 'Roboto Slab', serif;
        }
        .image-container {
            flex: 1;
            padding-right: 20px;
            text-align: center;
            height: 80%;
            max-height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Roboto Slab', serif;
        }
        .modal-content img {
            max-width: 100%;
            max-height: 100%;
            border-radius: 10px;
            object-fit: contain;
            font-family: 'Roboto Slab', serif;
        }
        .rock-title {
            font-weight: bold;
            font-size: 28px; 
            margin: 0;
            margin-bottom: 10px;
            text-align: center;
            font-family: 'Roboto Slab', serif;
        }
        .modal-message {
            flex: 1;
            font-family: 'Roboto Slab', serif;
        }
    `;
    
    document.head.appendChild(style);
}


// Trigger the loading screen when needed
document.getElementById('run-button').addEventListener('click', function() {
    // loadingScreen();

    const inputs = {
        latitude: centerPoint[1],
        longitude: centerPoint[0],
        mode: document.querySelector('input[name="mode-toggle"]:checked').value === "advanced",
        random_sampler: document.querySelector('input[name="quantum-toggle"]:checked').value === "quantum",
        desired_area: document.getElementById("area-text").value,                       // make sure this is set
        feedstock_surface_density: document.getElementById("feedstock-text").value,     // make sure this is set
        time_series_years: (document.getElementById("customSlider").value)*50 + 50,
        rock_type: document.getElementById("dropdown1").value,
        number_of_occurrences: document.getElementById("advanced-mode").checked ? document.getElementById("occurrences-text").value : 10
    };
    
    // TODO check feedstock & desired area is set, else display error message asking them to be set
    if (!inputs.feedstock_surface_density || !inputs.desired_area) {
       
        alert("must set the missing stuff");
        return false;
    }
    

   


    if (centerPoint) {
        // apicalls.sendCoordinates(inputs).then(serverResponse => {
        //     // serverResponse will be just the final server response
        //     data = serverResponse;
        //     console.log("aaa");
        //     console.log(serverResponse);
        //     showPopup();
        // });

        // start showing loading screen
        loaded = false;
        currentProgress = 0;
        loadingScreen();

        apicalls.sendCoordinates(inputs)
        .then(result => {
            console.log(result);
            data = result;
            console.log("aaa");
            loaded = true;
            clearInterval(prog_int_bar);
            clearInterval(factInterval);

            currentProgress = 100;
            prog_fill = document.getElementById('prog-bar');
            updateProgressBar(prog_fill, currentProgress);
            
            setTimeout(() => {
                // modalOverlay = document.getElementById('modal-overlay');
                // modalOverlay.style.display = 'none';
                modalOverlay.parentNode.removeChild(modalOverlay);
                // modalOverlay.display='none';
                // document.body.removeChild(modalOverlay);
                showPopup();

            }, 360); 
            

            

        }
        
        )
        .catch(error => console.error(error));

    }

});

let chart;

function formatTime(value) {
    return value;//.toFixed(2);//.toExponential(2);
}

function formatCa(value) {
    return value.toExponential(6);
}

        function showPopup() {
            document.getElementById('popup').classList.add('active');
            if (!chart) {
                createChart(data);  // Use the data from server response
            }
        }

        function hidePopup() {
            document.getElementById('popup').classList.remove('active');
        }

        function createChart(serverData) {
            const ctx = document.getElementById('timeSeriesChart').getContext('2d');

        

        // Find min and max for optimal scaling
        // const minCa = Math.min(...serverData["Ca++"]);
        // const maxCa = Math.max(...serverData["Ca++"]);
        // const range = maxCa - minCa;

        // // Create data points with indices for equal spacing
        // const dataPoints = serverData["Ca++"].map((value, index) => ({
        //     x: serverData["Time(yrs)"][index],
        //     y: value
        // }));
         // Multiply Ca++ values by 2 and find min/max
         document.getElementById('outtext').innerHTML = "Total CO2 removed in mol: " + serverData["graphdata"]["AUC_mean"] * 100;



         const multipliedCa = serverData["graphdata"]["Mean_Ca++"].map(value => value * 2 * serverData["graphdata"]["flow_rate"] * 10000);
         const minCa = Math.min(...multipliedCa);
         const maxCa = Math.max(...multipliedCa);
         const range = maxCa - minCa;

         const multipliedStdCa = serverData["graphdata"]["Std_Ca++"].map(value => value * 2 * serverData["graphdata"]["flow_rate"] * 10000);

         // Create data points with multiplied values
         const dataPoints = multipliedCa.map((value, index) => ({
             x: serverData["graphdata"]["Time(yrs)"][index],
             y: value
         }));

         // Create data points for error bounds
        const upperBound = multipliedCa.map((value, index) => ({
            x: serverData["graphdata"]["Time(yrs)"][index],
            y: value + multipliedStdCa[index]
        }));

        max_upper = Math.max(...upperBound);

        const lowerBound = multipliedCa.map((value, index) => ({
            x: serverData["graphdata"]["Time(yrs)"][index],
            y: value - multipliedStdCa[index]
        }));


        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [
                    {
                        label: 'Rate of removal of CO2 per m^2 per year',
                        data: dataPoints,
                        borderColor: 'rgb(88,129,87)',
                        backgroundColor: 'rgb(88,129,87)',
                        tension: 0.1,
                        pointRadius: 3,
                        borderWidth: 3
                    },
                    {
                        label: 'Upper bound',
                        data: upperBound,
                        borderColor: 'rgba(88,129,87,0.4)',
                        backgroundColor: 'rgba(88,129,87,0.3)',
                        tension: 0.1,
                        pointRadius: 0,
                        borderWidth: 1.5,
                        fill: 1  // Fill to the lower bound
                    },
                    {
                        label: 'Lower bound',
                        data: lowerBound,
                        borderColor: 'rgba(88,129,87,0.4)',
                        backgroundColor: 'rgba(88,129,87,0.3)',
                        tension: 0.1,
                        pointRadius: 0,
                        borderWidth: 1.5,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: 'linear',
                        title: {
                            display: true,
                            text: 'Time (years)'
                        },
                        ticks: {
                            stepSize: 1
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'CO2 (mol) / m^2 per year'
                        },
                        min: minCa - (range * 0.1),
                        max: max_upper + (range * 0.1),
                        ticks: {
                            callback: function(value) {
                                return value.toExponential(6);
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                if (context.datasetIndex === 0) {
                                    return `Rate of removal of CO2 ${context.raw.y.toExponential(6)} (mol) / m^2 per year`;
                                }
                                return '';  // Hide tooltips for     bounds
                            }
                        }
                    },
                    legend: {
                        labels: {
                            filter: function(item) {
                                // Only show the main line in legend
                                return item.text === 'Rate of removal of CO2 per m^2 per year';
                            }
                        }
                    }
                }
            }
        });

        //         datasets: [{
        //             label: 'Rate of removal of CO2 per m^2 per year',
        //             data: dataPoints,
        //             borderColor: 'rgb(88,129,87)',
        //             tension: 0.1,
        //             pointRadius: 3,
        //             borderWidth: 1.5
        //         }]
        //     },
        //     options: {
        //         responsive: true,
        //         scales: {
        //             x: {
        //                 type: 'linear',
        //                 title: {
        //                     display: true,
        //                     text: 'Time (years)'
        //                 },
        //                 ticks: {
        //                     stepSize: 1
        //                 }
        //             },
        //             y: {
        //                 title: {
        //                     display: true,
        //                     text: 'CO2 (mol) / m^2 per year'
        //                 },
        //                 min: minCa - (range * 0.1),
        //                 max: maxCa + (range * 0.1),
        //                 ticks: {
        //                     callback: function(value) {
        //                         return value.toExponential(6);
        //                     }
        //                 }
        //             }
        //         },
        //         plugins: {
        //             tooltip: {
        //                 callbacks: {
        //                     label: function(context) {
        //                         return `CO2: ${context.raw.y.toExponential(6)} (mol) / m^2 per year`;
        //                     }
        //                 }
        //             }
        //         }
        //     }
        // }); 

        
           
        }

        // Close popup when clicking outside
        document.getElementById('popup').addEventListener('click', function(e) {
            if (e.target === this) {
                hidePopup();
            }
        });


map.getCanvas().style.cursor = 'crosshair';