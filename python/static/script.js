mapboxgl.accessToken = 'pk.eyJ1Ijoia2F0Y3Jhd2ZvcmQiLCJhIjoiY203NXJ0ZTR6MDB3MzJucHo2ZmppNmR1YSJ9.KKea34jSVKuLRBfYQhSfJw';

const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/satellite-streets-v12',
    center: [-100, 42.76],
    zoom: 3
});

const layerList = document.getElementById('menu');
const inputs = layerList.getElementsByTagName('input');

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
    let progressInterval;
    let factInterval;

    const modalOverlay = document.createElement('div');
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

    function updateProgressBar(progressBarFill, value) {
        progressBarFill.style.width = value + '%';
    }

    function rotateFunFacts(funFacts, rockTitle, modalMessage, imageElement, currentIndex) {
        const rockKeys = Object.keys(funFacts);
        const currentRockKey = rockKeys[currentIndex];
        const currentRock = funFacts[currentRockKey];
        rockTitle.innerText = currentRockKey.charAt(0).toUpperCase() + currentRockKey.slice(1);
        modalMessage.innerText = currentRock.fact;
        imageElement.src = currentRock.image;
        return (currentIndex + 1) % rockKeys.length;
    }

    function progressBar1(rockInfo, progressIntervalTime = 3000, factIntervalTime = 5000) {
        console.log('');
        modalOverlay.style.display = 'flex';

        currentFactIndex = rotateFunFacts(rockInfo, rockTitle, modalMessage, rockImage, currentFactIndex);

        let currentProgress = 0;

        progressInterval = setInterval(() => {
            if (currentProgress >= totalProgress) {
                clearInterval(progressInterval);
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
    
    if (centerPoint) {
        apicalls.sendCoordinates(centerPoint[1], centerPoint[0]).then(serverResponse => {
            // serverResponse will be just the final server response
            data = serverResponse;
            console.log("aaa");
            console.log(serverResponse);
            showPopup();
        });

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
         const multipliedCa = serverData["Ca++"].map(value => value * 2);
         const minCa = Math.min(...multipliedCa);
         const maxCa = Math.max(...multipliedCa);
         const range = maxCa - minCa;

         // Create data points with multiplied values
         const dataPoints = multipliedCa.map((value, index) => ({
             x: serverData["Time(yrs)"][index],
             y: value
         }));


        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Rate of removal of CO2 per m^2 per year',
                    data: dataPoints,
                    borderColor: 'rgb(88,129,87)',
                    tension: 0.1,
                    pointRadius: 3,
                    borderWidth: 1.5
                }]
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
                        max: maxCa + (range * 0.1),
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
                                return `Ca++: ${context.raw.y.toExponential(6)} (mol) / m^2 per year`;
                            }
                        }
                    }
                }
            }
        });
            // const ctx = document.getElementById('timeSeriesChart').getContext('2d');
            
            //   // Calculate min and max for better scaling
            //   const caValues = serverData["Ca++"];
            //   const minCa = Math.min(...caValues);
            //   const maxCa = Math.max(...caValues);
            //   const range = maxCa - minCa;
              
            //   const dataPoints = serverData["Ca++"].map((value, index) => ({
            //     x: index,  // Use index for equal spacing
            //     y: value
            // }));

            // chart = new Chart(ctx, {
            //     type: 'line',
            //     data: {
            //         labels: serverData["Time(yrs)"],
            //         datasets: [{
            //             label: 'Ca++ vs Time',
            //             data: serverData["Ca++"],
            //             borderColor: 'rgb(75, 192, 192)',
            //             tension: 0.1,
            //             pointRadius: 3,
            //         }]
            //     },
            //     options: {
            //         responsive: true,
            //         scales: {
            //             x: {
            //                 type: 'logarithmic',
            //                 title: {
            //                     display: true,
            //                     text: 'Time (years)'
            //                 },
            //                 ticks: {
            //                     callback: function(value) {
            //                         return formatTime(value);
            //                     }
            //                 }
            //             },
            //             y: {
            //                 title: {
            //                     display: true,
            //                     text: 'Ca++ (mol/L)'
            //                 },
            //                 min: minCa - (range * 0.1),
            //                 max: maxCa + (range * 0.1),
            //                 ticks: {
            //                     callback: function(value) {
            //                         return formatCa(value);
            //                     }
            //                 }
            //             }
            //         },
            //         plugins: {
            //             tooltip: {
            //                 callbacks: {
            //                     label: function(context) {
            //                         return `Ca++: ${context.raw}`;
            //                     },
            //                     title: function(context) {
            //                         return `Time: ${formatTime(context[0].raw)}`;
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