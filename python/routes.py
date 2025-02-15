from flask import render_template, Blueprint, Flask, request, jsonify
from .crunchflow import hello
import os
import json

main_routes = Blueprint('main', __name__)

# def load_api_key():
#     with open('.secrets', 'r') as secrets_file:
#         for line in secrets_file:
#             if line.startswith('API_KEY'):
#                 return line.split('=')[1].strip()
#     return None




@main_routes.route('/')
def home():
    hello()
    return render_template('home.html')


@main_routes.route('/save_soil_data', methods=['POST'])
def save_soil_data():
    data = request.json
    print(data)
    # Ensure the quantum-deviation directory exists
    # os.makedirs('quantum-deviation', exist_ok=True)
    
    # # Write the JSON data to a file
    # file_path = os.path.join('quantum-deviation', 'soil_data.json')
    # with open(file_path, 'w') as f:
    #     json.dump(data, f, indent=2)
    
    return jsonify({"message": "Data saved successfully"}), 200
    

# @main_routes.route('/tst')
# def about():
#     return render_template('tst.html')