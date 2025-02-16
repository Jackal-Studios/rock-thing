

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


document.getElementById('run-button').addEventListener('click', function() {
    if (centerPoint) {
        apicalls.sendCoordinates(centerPoint[1], centerPoint[0]); // Note: latitude comes first
    }

    // const selectedRock = document.getElementById('dropdown1').value;
    // progressBar(selectedRock, 500, 2000); 
});

map.getCanvas().style.cursor = 'crosshair';