import os
import time
import random, string
import subprocess
import numpy as np
from flask import request, jsonify
import json
from quantumdeviation import quantum


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
                          feedspread, bulkdense, file_num, foldername):

    claydense = 2.65
    siltdense = 2.60
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
    
    rate = mineral_rates[feedstock][0]
    feeddense = mineral_rates[feedstock][1]
    # Perform calculations
    temp = temp - 273
    constant_flow = (precip / 1000) / 2
    soilclay_volfrac = (claypercent * claydense) / bulkdense
    soilsilt_volfrac = (siltpercent * siltdense) / bulkdense
    stock_volfrac = ((feedspread/10)/feeddense) / (bulkdense + ((feedspread/10)/feeddense))
    stock_clayfrac = ((claypercent * claydense) / (bulkdense + ((feedspread/10)/feeddense)))
    stock_siltfrac = ((siltpercent * siltdense) / (bulkdense + ((feedspread/10)/feeddense)))

    # Read the template file
    with open('aEWsoil.in', 'r') as file:
        content = file.read()

    # Make replacements
    content = content.replace('timeEWm.out 200', f'timeEWm{file_num}.out {years}')
    
    if feedstock != 'basalt':
        content = content.replace('An50Ab50AS', feedstock)
        content = content.replace('-rate 1.0e-13', f'-rate {rate:.2e}')
    
    content = content.replace('set_temperature 25.0', f'set_temperature {temp:.1f}')
    content = content.replace('constant_flow 0.0000158', f'constant_flow {constant_flow:.7f}')
    content = content.replace('8.9 cmol/kg', f'{cec:.1f} cmol/kg')
    
    # Replace in NativeSoil block
    native_soil_block = content.split('Condition NativeSoil')[1].split('end')[0]
    new_native_soil_block = native_soil_block.replace('Tracer', f'Tracer\n    {feedstock}')
    new_native_soil_block = new_native_soil_block.replace('Kaolinite                 0.0', f'Kaolinite                 {soilclay_volfrac:.6f}')
    new_native_soil_block += f'    K-feldspar               {soilsilt_volfrac:.6f}\n'
    content = content.replace(native_soil_block, new_native_soil_block)
    
    # Replace in Feedstock block
    feedstock_block = content.split('Condition Feedstock')[1].split('end')[0]
    new_feedstock_block = feedstock_block.replace('Tracer', f'Tracer\n    {feedstock}                  {stock_volfrac:.6f}')
    new_feedstock_block = new_feedstock_block.replace('Kaolinite                 0.0', f'Kaolinite                 {stock_clayfrac:.6f}')
    new_feedstock_block += f'    K-Feldspar               {stock_siltfrac:.6f}\n'
    content = content.replace(feedstock_block, new_feedstock_block)
    
    # Add K-Feldspar to MINERALS block
    minerals_block = content.split('MINERALS')[1].split('END')[0]
    new_minerals_block = minerals_block + 'K-Feldspar\n    -rate -13.00\n'
    content = content.replace(minerals_block, new_minerals_block)

    # Write the modified content to a new file
    with open(f'aEWsoil_{file_num}.in', 'w') as file:
        file.write(content)

    print(f"File 'aEWsoil_{file_num}.in' has been created successfully.")
    run_simulation(f'aEWsoil_{file_num}.in', foldername) 
    

# docker exec topcrunch-custom bash -c "cd /home/crunch_user/files && CrunchTope aEWbinary.in"
def run_simulation(input_file, foldername):
    return run_command(f'bash -c "cd /home/crunch_user/files/{foldername} && CrunchTope {input_file} && ls"')


def create_input_folder(foldername):
    print(f"input folder '{foldername}' creating...")
    create_user_folder(foldername)
    # return create_input_file(input_data, foldername)



def parse_output(foldername):
    print(f"getting output from: {foldername}")
    print(ls_user_folder(foldername))
    # TODO: loop through and calculate data
    data = read_and_package(f'/home/crunch_user/files/{foldername}/timeEW2m.out', ['Time(yrs)','pH', 'Ca++'])
    print(data)
    #clean up
    delete_user_folder(foldername)    
    return data
    

def get_output(soilgrids_data, weather_data, iterations):
    foldername = generate_unique_filename()
    create_input_folder(foldername)

    allData = quantum.runAll(soilgrids_data, weather_data, iterations)
    for i in range(iterations):
        create_input_file(allData["years"][i], allData["feedstock"][i], allData["clay"][i], allData["silt"][i], allData["temperature"][i], allData["precipitation"][i], allData["cec"][i], allData["spread"][i], allData["bulkdense"], i, foldername)
        run_simulation(foldername) 
    return parse_output(foldername)    # run crunchtop

def handle_json_request(data):
    # do stuff
    # send stuff like this get_output(soilgrids_data, weather_data, iterations)

    # for testing:
    return read_and_package(f'/home/crunch_user/files/timeEW2m.out', ['Time(yrs)','pH', 'Ca++'])
