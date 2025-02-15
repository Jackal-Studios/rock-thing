# from flask import Flask
# from .routes import main_routes  # Importing routes (views)
# from flask import render_template, Blueprint

# main_routes = Blueprint('main', __name__)

# @main_routes.route('/')
# def home():
#     return render_template('home.html')

# @main_routes.route('/about')
# def about():
#     return render_template('about.html')

# app = Flask(__name__)

# # @app.route('/')
# # def hello_world():
# #     return 'Hello, World!'

# if __name__ == '__main__':
#     # app.config.from_object('config.Config')
#     app.register_blueprint(main_routes)
#     app.run(debug=True)


from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)