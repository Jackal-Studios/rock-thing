import os
import time
import random, string
import subprocess
import numpy as np
from flask import request, jsonify
import json


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

def create_input_file(input_data, foldername):
    # create here : f'/home/crunch_user/files/{foldername}'
    # pass input_data to kats math stuff and get dictionary
    # create file#1 from dicitionary
    # run 

    #TODO implement this
    # print("make the input file")
    # return run_command(f'bash -c "cd /home/crunch_user/files/{foldername} && cp ../aEWbinary.in . && ls"')
    return 0


    

# docker exec topcrunch-custom bash -c "cd /home/crunch_user/files && CrunchTope aEWbinary.in"
def run_simulation(input_data, foldername, inputfilename):
    #run inputfile through kats math -> get dictionary
    # loop over dictionary changing inputfiles and end up with 10 time files
    # create_input_file()
    return run_command(f'bash -c "cd /home/crunch_user/files/{foldername} && CrunchTope {inputfilename} && ls"')


def create_input_folder(foldername):
    print(f"input folder '{foldername}' creating...")
    create_user_folder(foldername)
    # return create_input_file(input_data, foldername)



def parse_output(foldername):
    print(f"getting output from: {foldername}")
    print(ls_user_folder(foldername))
    # loop through and calculate data
    data = read_and_package(f'/home/crunch_user/files/{foldername}/timeEW2m.out', ['Time(yrs)','pH', 'Ca++'])
    print(data)

    #clean up
    delete_user_folder(foldername)    
    return data
    

def get_output(input_data):
    foldername = generate_unique_filename()
    create_input_folder(foldername)
    # loop over
    run_simulation(input_data, foldername, "aEWbinary.in")  #TODO change this ?
    # print("input folder created")
    # return parse_output(foldername)    # run crunchtop
    return read_and_package(f'/home/crunch_user/files/timeEW2m.out', ['Time(yrs)','pH', 'Ca++'])
