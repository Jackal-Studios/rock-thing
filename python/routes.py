from flask import render_template, Blueprint
from flask import request, jsonify
import subprocess
import crunchflow

main_routes = Blueprint('main', __name__)



# @main_routes.route('/run')
# def run_script():
#     client = docker.from_env()
#     container = client.containers.get('topcrunch-custom')
    
#     if isinstance(commands, str):
#         commands = [commands]
    
#     results = {}
#     for cmd in commands:
#         result = container.exec_run(cmd)
#         results[cmd] = {
#             'exit_code': result.exit_code,
#             'output': result.output.decode('utf-8')
#         }
#     print(result)
#     return result

# docker exec topcrunch-custom bash -c "cd /home/crunch_user/files && CrunchTope aEWbinary.in"
@main_routes.route('/run')
def run_script():
    try:
        # Example command to run in gcc-service
        command = f'docker exec topcrunch-custom bash -c "cd /home/crunch_user/files && ls"'
        
        # Run the command and capture output
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        
        # Return the results
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
    

@main_routes.route('/run1')
def run_script2():
    return crunchflow.create_user_folder("1HELLLO")
    # return crunchflow.run_command('bash -c "cd /home/crunch_user && ls"')

@main_routes.route('/rundel')
def run_script3():
    return crunchflow.delete_user_folder("1HELLLO")
    # return crunchflow.run_command('bash -c "cd /home/crunch_user && ls"')
@main_routes.route('/runcrfol')
def run_script4():
    return crunchflow.create_input_folder(1, crunchflow.generate_unique_filename())
    
@main_routes.route('/runparseout')
def run_script5():
    return crunchflow.get_output(1)      
    
@main_routes.route('/ls')
def run_script6():
    return crunchflow.ls_user_folder("")      
    

@main_routes.route('/')
def home():
    crunchflow.hello()
    return render_template('home.html')


@main_routes.route('/save_soil_data', methods=['POST'])
def save_soil_data():
    data = request.json
    # print(data)
    # sent the output to the parse output and return

    # resp = crunchflow.get_output(data)
    resp = crunchflow.handle_json_request(data)

    return resp

@main_routes.route('/save_data', methods=['POST'])
def save_data():
    data = request.json
    # print(data)
    # sent the output to the parse output and return

    # resp = crunchflow.get_output(data)
    # resp = crunchflow.handle_json_request(data)
    resp = crunchflow.handle_json_request(data)

    return resp
    

# @main_routes.route('/tst')
# def about():
#     return render_template('tst.html')