from flask import Flask
from .routes import main_routes  # Importing routes (views)

def create_app():
    app = Flask(__name__)

    # Set up configurations (can use environment variables, config.py, etc.)
    # app.config.from_object('config.cf')

    # Register blueprints (if you have multiple route files)
    app.register_blueprint(main_routes)

    return app