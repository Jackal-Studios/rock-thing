
from app import create_app
from apicalls import apicalls_bp

app = create_app()

app.register_blueprint(apicalls_bp)

if __name__ == '__main__':
    app.run(debug=True)