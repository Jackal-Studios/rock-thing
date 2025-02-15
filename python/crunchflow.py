import os
import time
import random, string
import subprocess
from flask import request, jsonify

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
    #TODO implement this
    print("make the input file")
    return run_command(f'bash -c "cd /home/crunch_user/files/{foldername} && cp ../aEWbinary.in . && ls"')


    

# docker exec topcrunch-custom bash -c "cd /home/crunch_user/files && CrunchTope aEWbinary.in"
def run_simulation(foldername, inputfilename):
    return run_command(f'bash -c "cd /home/crunch_user/files/{foldername} && CrunchTope {inputfilename} && ls"')


def create_input_folder(input_data, foldername):
    print(f"input folder '{foldername}' creating...")
    create_user_folder(foldername)
    return create_input_file(input_data, foldername)



def parse_output(foldername):
    print(f"getting output from: {foldername}")
    print(ls_user_folder(foldername))

    # TODO: parse output data

    # clean up
    return delete_user_folder(foldername)
    

def get_output(input_data):
    foldername = generate_unique_filename()
    create_input_folder(input_data, foldername)
    run_simulation(foldername, "aEWbinary.in")  #TODO change this ?
    # print("input folder created")
    return parse_output(foldername)    # run crunchtop