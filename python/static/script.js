mapboxgl.accessToken = 'pk.eyJ1Ijoia2F0Y3Jhd2ZvcmQiLCJhIjoiY203NXJ0ZTR6MDB3MzJucHo2ZmppNmR1YSJ9.KKea34jSVKuLRBfYQhSfJw';

const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/satellite-streets-v12',
    center: [-91.874, 42.76],
    zoom: 0
});

const layerList = document.getElementById('menu');
const inputs = layerList.getElementsByTagName('input');

for (const input of inputs) {
    input.onclick = (layer) => {
        const layerId = layer.target.id;
        map.setStyle('mapbox://styles/mapbox/' + layerId);
    };
}

let centerPoint = null;
let radiusCircle = null;
let isDragging = false;

const rockInfo = {
    basalt: "Basalt: A volcanic rock widely used in ERW due to its availability and effectiveness in capturing carbon dioxide. It can sequester up to 2 tons of CO2 per hectare per year.",
    olivine: "Olivine: A magnesium and iron-rich rock that weathers quickly, providing fast carbon sequestration. It can capture up to 5 tons of CO2 per hectare per year.",
    serpentinite: "Serpentinite: A magnesium-rich rock high in nickel, capable of capturing up to 0.5 tons of CO2 per hectare per year.",
    wollastonite: "Wollastonite: A calcium silicate mineral found in skarns, which has potential for CO2 sequestration.",
    glauconite: "Glauconite: Also known as greensand, this iron potassium phyllosilicate has known plant nutritional properties and is effective in capturing carbon.",
    kimberlite: "Kimberlite: A mineralogically complex feedstock with vast capacities to sequester carbon dioxide.",
    brucite: "Brucite: A magnesium hydroxide mineral that can be used as a feedstock for ERW.",
    feldspar: "Feldspar: A group of rock-forming tectosilicate minerals that can release potassium during weathering.",
    apatite: "Apatite: A phosphate mineral that can release phosphorus during weathering, potentially reducing the need for chemical fertilizers."
};

function createRadiusCircle(radius) {
    const options = { steps: 64, units: 'kilometers' };
    return turf.circle(centerPoint, radius, options);
}

map.on('click', (e) => {
    if (isDragging) {
        isDragging = false;
        map.off('mousemove', updateCircle);
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

    map.on('mousemove', updateCircle);
    isDragging = true;
});

function updateCircle(e) {
    if (!isDragging) return;
    const newPoint = turf.point([e.lngLat.lng, e.lngLat.lat]);
    const from = turf.point(centerPoint);
    const distance = turf.distance(from, newPoint, { units: 'kilometers' });

    radiusCircle = createRadiusCircle(distance);
    map.getSource('circle').setData(radiusCircle);

    const info = document.getElementById('circle-info');
    info.innerHTML = `<p><strong>Radius:</strong> ${distance.toFixed(2)} km</p><p><strong>Center:</strong> [${centerPoint[0].toFixed(6)}, ${centerPoint[1].toFixed(6)}]</p>`;
}

document.getElementById('run-button').addEventListener('click', function() {
    const selectedRock = document.getElementById('dropdown1').value;
    const message = rockInfo[selectedRock];
    const modalMessage = document.getElementById('modal-message');
    modalMessage.innerText = message;
    const modal = document.getElementById('modal');
    modal.style.display = 'block';
});