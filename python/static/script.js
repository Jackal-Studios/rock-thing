

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
                'fill-color': '#007cbf',
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

let data;
document.getElementById('run-button').addEventListener('click', function() {
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
            
              // Calculate min and max for better scaling
              const caValues = serverData["Ca++"];
              const minCa = Math.min(...caValues);
              const maxCa = Math.max(...caValues);
              const range = maxCa - minCa;
              
              const dataPoints = serverData["Ca++"].map((value, index) => ({
                x: index,  // Use index for equal spacing
                y: value
            }));

            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: serverData["Time(yrs)"],
                    datasets: [{
                        label: 'Ca++ vs Time',
                        data: serverData["Ca++"],
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1,
                        pointRadius: 3,
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            type: 'logarithmic',
                            title: {
                                display: true,
                                text: 'Time (years)'
                            },
                            ticks: {
                                callback: function(value) {
                                    return formatTime(value);
                                }
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Ca++ (mol/L)'
                            },
                            min: minCa - (range * 0.1),
                            max: maxCa + (range * 0.1),
                            ticks: {
                                callback: function(value) {
                                    return formatCa(value);
                                }
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `Ca++: ${context.raw}`;
                                },
                                title: function(context) {
                                    return `Time: ${formatTime(context[0].raw)}`;
                                }
                            }
                        }
                    }
                }
            });
        }

        // Close popup when clicking outside
        document.getElementById('popup').addEventListener('click', function(e) {
            if (e.target === this) {
                hidePopup();
            }
        });


map.getCanvas().style.cursor = 'crosshair';