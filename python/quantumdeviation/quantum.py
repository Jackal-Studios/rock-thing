import numpy as np
import json
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import requests
import random

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/era5"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

def getQuantumSample(n, left, mode, right):

    data = np.random.triangular(left, mode, right, 10000)

    num_of_bins = 200

    bin_counts, bin_edges = np.histogram(data, bins=num_of_bins, density=True)
    bin_count_sum = np.sum(bin_counts)
    centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    new_list = []
    for count, center in zip(bin_counts, centers):
        how_many = int(count / bin_count_sum * num_of_bins * 5)
        new_list.extend([center] * how_many)

    def quantum_random_int(max_value):
        num_qubits = (max_value - 1).bit_length()
        circuit = QuantumCircuit(num_qubits)
        circuit.h(range(num_qubits))
        circuit.measure_all()
        
        simulator = AerSimulator()
        result = simulator.run(circuit, shots=1).result()
        counts = result.get_counts()
        
        random_bin = list(counts.keys())[0]
        random_int = int(random_bin, 2)
        
        return min(random_int, max_value)

    def quantum_random_sample(data_list, n):
        selected_samples = [data_list[quantum_random_int(len(data_list)-1)] for _ in range(n)]
        return selected_samples

    random_samples = quantum_random_sample(new_list, n)

    return random_samples

def getClassicalSample(n, left, mode, right):
    data = np.random.triangular(left, mode, right, n)
    return data[:n]

def getRandomSample(n, left, mode, right, quantum):
    if quantum:
        return getQuantumSample(n, left, mode, right)
    return getClassicalSample(n, left, mode, right)

def get_archived_weather(lat, long, start, end, metrics):
    """
    Returns historical weather data for a given latitude and longitude, time range, and set of metrics.

    Args:
    lat (float): Latitude of location.
    long (float): Longitude of location.
    start (str): Start date in YYYY-MM-DD format.
    end (str): End date in YYYY-MM-DD format.
    metrics (list): List of weather metrics to retrieve (https://open-meteo.com/en/docs for more details).

    Returns:
    dict: Dictionary containing weather data, with latitude and longitude as separate keys and weather metrics as sub-dictionaries.
    """
    metrics = ','.join(metrics)
    filter = f'latitude={lat}&longitude={long}&hourly={metrics}&start_date={start}&end_date={end}'
    r = requests.get(ARCHIVE_URL + '?' + filter)
    d = r.json()

    return {**{'latitude': d['latitude'], 'longitude': d['longitude']}, **d['hourly']}

def get_distance(lon1, lat1, lon2, lat2):
    """
    Returns the distance, in kilometers, between two sets of longitude/latitude coordinates.

    Args:
    lon1 (float): Longitude of first location.
    lat1 (float): Latitude of first location.
    lon2 (float): Longitude of second location.
    lat2 (float): Latitude of second location.

    Returns:
    float: The distance, in kilometers, between the two sets of coordinates.
    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    newlon = lon2 - lon1
    newlat = lat2 - lat1

    haver_formula = np.sin(newlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(newlon/2.0)**2
    km = 6367 * 2 * np.arcsin(np.sqrt(haver_formula ))

    return km

def classify_biome_and_climate(lat, lon):

    biome_data = {
        "tropical_rainforest": {
            "latitude_range": [-23.5, 23.5],
            "temperature_range_C": [20, 30],
            "precipitation_range_mm": [2000, 4000]
        },
        "tropical_savanna": {
            "latitude_range": [-23.5, 23.5],
            "temperature_range_C": [18, 30],
            "precipitation_range_mm": [500, 1500]
        },
        "desert": {
            "latitude_range": [-30, 30],
            "temperature_range_C": [20, 40],
            "precipitation_range_mm": [0, 250]
        },
        "temperate_grassland": {
            "latitude_range": [30, 50],
            "temperature_range_C": [-5, 20],
            "precipitation_range_mm": [500, 900]
        },
        "temperate_broadleaf_forest": {
            "latitude_range": [30, 50],
            "temperature_range_C": [-10, 20],
            "precipitation_range_mm": [750, 1500]
        },
        "boreal_forest": {
            "latitude_range": [50, 70],
            "temperature_range_C": [-30, 15],
            "precipitation_range_mm": [200, 750]
        },
        "tundra": {
            "latitude_range": [60, 80],
            "temperature_range_C": [-40, 10],
            "precipitation_range_mm": [150, 300]
        },
        "mediterranean": {
            "latitude_range": [30, 45],
            "temperature_range_C": [10, 25],
            "precipitation_range_mm": [300, 750]
        }
    }

    def get_biome(lat, lon):
        for biome, data in biome_data.items():
            if data["latitude_range"][0] <= lat <= data["latitude_range"][1]:
                return biome
        return "unknown"

    biome = get_biome(lat, lon)
    
    if biome != "unknown":

        temp_range = biome_data[biome]["temperature_range_C"]
        precip_range = biome_data[biome]["precipitation_range_mm"]

        return {
            "temperature": random.randint(temp_range[0], temp_range[1]),
            "precipitation": random.randint(precip_range[0], precip_range[1])
        }
    
    else:
        return {
            "temperature": random.randint(0,20),
            "precipitation": random.randint(0,4000)
        }

def callWeather(lat, long):

    start = '2023-01-01'
    end = '2024-01-01'
    metrics = ['temperature', 'precipitation'] #temperature -> celsius, precipiration -> mm

    new_data = {}

    try:
        data = get_archived_weather(lat, long, start, end, metrics)
    except:
        start = '2022-01-01'
        end = '2023-01-01'
        try:
            data = get_archived_weather(lat, long, start, end, metrics)
        except:
            data = classify_biome_and_climate(lat, long)

    temp = data['temperature']
    precipitation = data['precipitation']

    minimum = min(temp)
    maximum = max(temp)
    mean = sum(temp) / len(temp)
    new_data["temperature"] = [minimum, mean, maximum]

    minimum = min(precipitation)
    maximum = max(precipitation)
    mean = sum(precipitation) / len(precipitation)
    new_data["precipitation"] = [minimum, mean, maximum]

    return new_data

def runAll(soiljson, weatherjson, n, quantum, feedstock, spread, years, lat, lon):

    tempPrecipData = callWeather(lat, lon)
    
    samples = {}

    for layer in soiljson["properties"]["layers"]:
        property_name = layer["name"]
        values = layer["depths"][0]["values"]
        left, mode, right = values["Q0.05"], values["Q0.5"], values["Q0.95"]
        soil_samples = getRandomSample(n, left, mode, right, quantum)
        samples[property_name] = soil_samples

    weather_result = weatherjson['result'][0]

    #precipitation
    precipitation_stats = tempPrecipData['precipitation']
    precip_samples = getRandomSample(n, precipitation_stats[0], precipitation_stats[1], precipitation_stats[2], quantum)
    samples["precipitation"] = precip_samples

    #temperature
    temp_stats = tempPrecipData['temperature']
    temp_samples = getRandomSample(n, temp_stats[0], temp_stats[1], temp_stats[2], quantum)

    for temp in range(len(temp_samples)):
        if temp_samples[temp] < 25:
            temp_samples[temp] = 25
    
    samples["temperature"] = temp_samples

    feedstockList = []
    spreadList = []
    yearList = []

    for _ in range(n):
        feedstockList.append(feedstock)
        spreadList.append(spread)
        yearList.append(years)

    samples["feedstock"] = feedstockList
    samples["spread"] = spreadList
    samples["years"] = yearList

    return samples

"""
with open('soilgridall.json', 'r') as file:
    soilgrids_data = json.load(file)

with open('weather.json', 'r') as file:
    weather_data = json.load(file)

n = 10
quantum = True #uses quantum?
feedstock = "basalt"
spread = 10
years = 50

#note: does not use area

output = runAll(soilgrids_data, weather_data, n, quantum, feedstock, spread, years)
print(output)
"""
