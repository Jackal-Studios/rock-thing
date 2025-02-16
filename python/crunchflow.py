import os
import time
import random, string
import subprocess
import numpy as np
from flask import request, jsonify
import json
from quantumdeviation import quantum
from scipy.interpolate import interp1d


def hello():
    print("hi")


def run_command(command):
    try:
        full_command = f"docker exec topcrunch-custom {command}"
        result = subprocess.run(
            full_command,
            shell=True,
            capture_output=True,
            text=True
        )
        print(result)
        
        return jsonify({
            'success': True,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'exit_code': result.returncode
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



def read_and_package(file_path, columns):
    # Load data, skip first line (metadata) and header line
    data = np.loadtxt(file_path, skiprows=2)
    
    # Get column indices (based on the file format you showed)
    column_indices = {
        'Time(yrs)': 0,
        'pH': 1,
        'H+': 2,
        'CO2(aq)': 3,
        'Mg++': 4,
        'Ca++': 5
    }
    
    # Create dictionary with requested columns
    result = {
        col: data[:, column_indices[col]].tolist()
        for col in columns
    }
    
    return json.dumps(result)


def create_user_folder(foldername):
    return run_command(f'bash -c "cd /home/crunch_user/files && mkdir -p {foldername} && cp *.dbs {foldername}/ && ls {foldername}"')

def delete_user_folder(foldername):
    return run_command(f'bash -c "cd /home/crunch_user/files && rm -rf {foldername} && ls /home/crunch_user/files"')

def ls_user_folder(foldername):
    return run_command(f'bash -c "cd /home/crunch_user/files/{foldername} && ls"')




def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

def current_milli_time():
    return round(time.time() * 1000)

def generate_unique_filename():
    return str(current_milli_time()) + randomword(10)

def create_input_file(years, feedstock, claypercent, siltpercent, temp, precip, cec, 
                          feedspread, bulkdense, file_num, foldername, sandpercent):

    claydense = 2.65
    siltdense = 2.60
    sanddense = 2.65
    # rates and density for feedstocks
    mineral_rates = {
        "Basalt": (-13.00, 3.01),
        "HCl(c)": (-10.00, 1.03),
        "CO2_pump": (-6.00, 1.98),
        "HNO3(c)": (-10.00, 1.51),
        "Cs-Illite": (-5.00, 275),
        "Gypsum": (-6.00, 2.3),
        "Calcite": (-6.19, 2.71),
        "Pyrite": (-8.00, 5),
        "Vivianite": (-8.0, 2.65),
        "Hydroxylapatite": (-11.0, 3.05),
        "Katoite": (-9, 2.79),
        "Portlandite": (-9, 2.23),
        "Aragonite": (-8.10, 2.93),
        "Dolomite": (-7.70, 2.84),
        "Magnesite": (-9.40, 3.05),
        "Siderite": (-8.90, 3.96),
        "Iron": (-11.30, 7.86),
        "Muscovite": (-13.00, 2.85),
        "Quartz": (-13.39, 2.65),
        "Kaolinite": (-13.00, 2.65),
        "Ilmenite": (-13.00, 4.45),
        "K-Feldspar": (-13.00, 2.60),
        "Gibbsite": (-10.00, 2.34),
        "Chalcedony": (-13.39, 2.62),
        "Ettringite": (-8.00, 1.80),
        "Chrysocolla": (-7.00, 2.10),
        "Goethite": (-7.00, 4.0),
        "Jarosite": (-6.00, 3.25),
        "Jurbanite": (-6.00, 1.79),
        "Alunite": (-7.00, 2.75),
        "Wollastonite": (-13.00, 2.84),
        "Larnite": (-13.00, 3.28)
    }

    # feedstock ="Larnite"
    
    rate = mineral_rates[feedstock.title()][0]
    feeddense = mineral_rates[feedstock.title()][1]

    print(rate)
    print(feeddense)

    # Perform calculations
    temp = temp - 273
    constant_flow = precip / 2 #(precip / 1000) / 2  TODO update with new weather
    soilclay_volfrac = (claypercent * claydense) / bulkdense
    soilsilt_volfrac = (siltpercent * siltdense) / bulkdense
    soilsand_volfrac = (sandpercent * sanddense) / bulkdense
    stock_volfrac = ((float(feedspread)/10)/float(feeddense)) / (bulkdense + ((float(feedspread)/10)/float(feeddense)))
    stock_clayfrac = ((claypercent * claydense) / (bulkdense + ((float(feedspread)/10)/float(feeddense))))
    stock_siltfrac = ((siltpercent * siltdense) / (bulkdense + ((float(feedspread)/10)/float(feeddense))))
    stock_sandfrac = ((sandpercent * sanddense) / (bulkdense + ((float(feedspread)/10)/float(feeddense))))

    stock_sandfrac = round((stock_sandfrac / 100), 3)
    stock_siltfrac/= 100
    stock_clayfrac/= 100
    stock_volfrac/= 100
    soilsand_volfrac/= 100
    soilsilt_volfrac/= 100
    soilclay_volfrac /= 100

    #normalize
    # tot = soilsand_volfrac + soilsilt_volfrac + soilclay_volfrac
    # soilsand_volfrac /=tot
    # soilsilt_volfrac /=tot
    # soilclay_volfrac /=tot


    # Read the template file
    # with open('/home/crunch_user/files/aEWsoil.in', 'r') as file:
    #     content = file.read()
    print("reading lines")
    with open('/home/crunch_user/files/aEWsoil.in', "r") as file:
        lines = file.readlines()

    print("read lines")
    years = 200
    lines[28] = f"time_series    timeEWm{file_num}.out {years}\n"

    # does float work?
    if(temp > 25):
        lines[53] = f"set_temperature {temp:.1f}\n"
    
    # if constant_flow < 0.1:
    constant_flow = 0.2
    lines[84] = f'constant_flow   {constant_flow:.1f}\n'

    lines[92] = f'{cec:.1f} cmol/kg\n'

    if(feedstock.lower() == "basalt"):
        feedstock = 'An50Ab50AS'


    #35 padding should be 
    lines[145] = f"{feedstock}"
    len_rock = len(feedstock)
    while(35 - len_rock != 0):
        lines[145] += " "
        len_rock += 1
    lines[145] += f"{stock_volfrac:.9f} ssa  0.5\n" 

    lines[147] = lines[147][:35]  + f"{stock_clayfrac:.9f} ssa 0.1\n"
    
    lines[148] = lines[148][:35]  + f"{stock_siltfrac:.9f} ssa 0.1\n"
    lines[149] = lines[149][:35]  + f"{stock_sandfrac:.9f} ssa 0.1\n"

    # TODO maybe line 157 temperature      25


    # Condition NativeSoil  !Same water as above.
    lines[173] = f"{feedstock}"
    len_rock = len(feedstock)
    while(35 - len_rock != 0):
        lines[173] += " "
        len_rock += 1

    lines[173] += f"0.00 ssa  3\n" 
    lines[174] = lines[174][:35]  + f"{soilclay_volfrac:.9f} ssa 1\n"      #TODO change to 0.1
    lines[175] = lines[175][:35]  + f"{soilsilt_volfrac:.9f} ssa 0.1\n"
    lines[176] = lines[176][:35]  + f"{soilsand_volfrac:.9f} ssa 0.1\n"

    # line 133 temp?

    
    # # Replace in NativeSoil block
    # # line 43
    # # line 146
    # # line 175
    # # line 213
    
    lines[34] = f"{feedstock}"
    len_rock = len(feedstock)
    while(13 - len_rock != 0):
        lines[34] += " "
        len_rock += 1

    lines[34] += f"-label default  -rate  {rate:.2f} !DissolutionOnly\n"

    #line 38 change K-feldspar rate ???
        # new_minerals_block = minerals_block + 'K-Feldspar\n    -rate -13.00\n'


    # Write the modified content to a new file
    # with open(f'/home/crunch_user/files/{foldername}/aEWsoil_{file_num}.in', 'w') as file:
    #     file.write(content)

    with open(f'/home/crunch_user/files/{foldername}/aEWsoil_{file_num}.in', "w") as file:
        file.writelines(lines)

    print(f"current folder status {file_num}:")
    # print(ls_user_folder(foldername))
    print(f"File '/home/crunch_user/files/{foldername}/aEWsoil_{file_num}.in' has been created successfully.")    
    run_simulation(f'aEWsoil_{file_num}.in', foldername) 
    

# docker exec topcrunch-custom bash -c "cd /home/crunch_user/files && CrunchTope aEWbinary.in"
def run_simulation(input_file, foldername):
    return run_command(f'bash -c "cd /home/crunch_user/files/{foldername} && CrunchTope {input_file} && ls"')


def create_input_folder(foldername):
    print(f"input folder '{foldername}' creating...")
    create_user_folder(foldername)
    # return create_input_file(input_data, foldername)



# def parse_output(foldername):
#     print(f"getting output from: {foldername}")
#     print(ls_user_folder(foldername))
#     # TODO: loop through and calculate data
#     data = read_and_package(f'/home/crunch_user/files/{foldername}/timeEW2m.out', ['Time(yrs)','pH', 'Ca++'])
#     print(data)
#     #clean up
#     delete_user_folder(foldername)    
#     return data

def parse_output(n, foldername):
    print(f"Gathering output from: {foldername}")

    # Lists to store time, pH, and Ca++ values for each iteration
    time_arrays = []
    pH_arrays = []
    Ca_arrays = []

    for i in range(n):  # Loop through each iteration output file
        file_path = f'/home/crunch_user/files/{foldername}/timeEWm{i}.out'
        data_json = read_and_package(file_path, ['Time(yrs)', 'pH', 'Ca++'])
        data = json.loads(data_json)  # Convert JSON string back to dictionary

        time = np.array(data['Time(yrs)'])
        pH = np.array(data['pH'])
        Ca = np.array(data['Ca++'])

        # Interpolate all curves to a common time scale
        if len(time_arrays) == 0:
            common_time = np.linspace(min(time), max(time), 100)  # Define common time points

        pH_interp = interp1d(time, pH, kind='linear', fill_value="extrapolate")
        Ca_interp = interp1d(time, Ca, kind='linear', fill_value="extrapolate")

        # Store interpolated values
        time_arrays.append(common_time)
        pH_arrays.append(pH_interp(common_time))
        Ca_arrays.append(Ca_interp(common_time))

    # Convert lists to numpy arrays for easy computation
    pH_arrays = np.array(pH_arrays)  # Shape: (n_iterations, 100)
    Ca_arrays = np.array(Ca_arrays)  # Shape: (n_iterations, 100)

    # Compute mean and standard deviation across iterations
    mean_pH = np.mean(pH_arrays, axis=0)
    std_pH = np.std(pH_arrays, axis=0)

    mean_Ca = np.mean(Ca_arrays, axis=0)
    std_Ca = np.std(Ca_arrays, axis=0)

    # Package results into a dictionary
    result = {
        "Time(yrs)": common_time.tolist(),
        "Mean_pH": mean_pH.tolist(),
        "Std_pH": std_pH.tolist(),
        "Mean_Ca++": mean_Ca.tolist(),
        "Std_Ca++": std_Ca.tolist()
    }

    # Clean up folder
    # delete_user_folder(foldername)

    return json.dumps(result)



def get_output(soilgrids_data, weather_data, iterations, is_quantum, feedstock, spread, years):
    # bulkdensity = allData["bdod"]
    foldername = generate_unique_filename()
    create_input_folder(foldername)
    print("running algorithms #")
    allData = quantum.runAll(soilgrids_data, weather_data, iterations, is_quantum, feedstock, spread, years)
    # print("ALL DATA:")
    print(allData)
    print("############################################################")
    for i in range(iterations):
        print(i)
        create_input_file(allData["years"][i], allData["feedstock"][i], allData["clay"][i], allData["silt"][i], allData["temperature"][i], allData["precipitation"][i], allData["cec"][i], allData["spread"][i], allData["bdod"][i], i, foldername, allData["sand"][i])
    return parse_output(iterations, foldername)    # run crunchtop        run_simulation(foldername) 


def handle_json_request(data):
    # do stuff
    # send stuff like this get_output(soilgrids_data, weather_data, iterations, is_quantum, feedstock, spread, years)
    print(data) #get_output(soilgrids_data, weather_data, iterations, is_quantum, feedstock, spread, years)
    inputs = data['inputs']
    # weather_data = data['weatherData']
    with open('quantumdeviation/weather.json', 'r') as file:
        weather_data = json.load(file)
    # print(weather_data)
    print(inputs.get('number_of_occurrences'))
    print(f"feedstockden:{inputs.get('feedstock_surface_density')}")
    out = get_output(data['soilData'], weather_data ,inputs.get('number_of_occurrences'), inputs.get('mode'), inputs.get('rock_type'), inputs.get('feedstock_surface_density'), inputs.get('time_series_years'))
    # return read_and_package(f'/home/crunch_user/files/timeEW2m.out', ['Time(yrs)','pH', 'Ca++'])
    return out
    # for testing:
    # return read_and_package(f'/home/crunch_user/files/timeEW2m.out', ['Time(yrs)','pH', 'Ca++'])
