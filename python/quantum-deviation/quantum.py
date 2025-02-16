import numpy as np
import json
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

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

def runAll(soiljson, weatherjson, n, quantum):
    
    samples = {}

    for layer in soiljson["properties"]["layers"]:
        property_name = layer["name"]
        values = layer["depths"][0]["values"]
        left, mode, right = values["Q0.05"], values["Q0.5"], values["Q0.95"]
        soil_samples = getRandomSample(n, left, mode, right, quantum)
        samples[property_name] = soil_samples

    weather_result = weatherjson['result'][0]

    #precipitation
    precipitation_stats = weather_result['precipitation']

    left, mode, right = precipitation_stats["min"], precipitation_stats["mean"], precipitation_stats["max"]

    precip_samples = getRandomSample(n, left, mode, right, quantum)

    samples["precipitation"] = precip_samples

    #temperature
    temp_stats = weather_result['temp']

    left, mode, right = temp_stats["record_min"], temp_stats["mean"], temp_stats["record_max"]

    temp_samples = getRandomSample(n, left, mode, right, quantum)

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
