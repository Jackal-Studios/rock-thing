from flask import render_template, Blueprint
from .crunchflow import hello

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
    

# @main_routes.route('/tst')
# def about():
#     return render_template('tst.html')