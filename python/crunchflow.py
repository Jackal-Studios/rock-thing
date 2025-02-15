
def hello():
    print("hi")

def create_input_file(input_data, filename):
    print("input file creating...")

def parse_output(filename):
    print("getting output")
    # clean up
    return {}

def get_output(input_data):
    filename = "uniquename"
    create_input_file(input_data, filename)
    print("input file created")
    # run crunchtop

    return parse_output(filename)