from flask import render_template, Blueprint

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def home():
    return render_template('home.html')

# @main_routes.route('/tst')
# def about():
#     return render_template('tst.html')