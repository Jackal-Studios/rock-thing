import os
import time
import random, string


def hello():
    print("hi")

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

def current_milli_time():
    return round(time.time() * 1000)

def generate_unique_filename():
    return str(current_milli_time()) + randomword(10)

def create_input_file(input_data, filename):
    print("input file creating...")
    
def parse_output(filename):
    print("getting output")

    #parse output data

    # clean up
    os.remove(filename)
    return {}

def get_output(input_data):
    filename = generate_unique_filename()
    create_input_file(input_data, filename)
    print("input file created")
    return parse_output(filename)    # run crunchtop