from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load your secret API key securely
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

@app.route('/api/get-soil-weather', methods=['POST'])
def get_soil_weather():
    data = request.get_json()
    lat = data.get('latitude')
    lng = data.get('longitude')

    try:
        # 1. Call Soil API (no key required)
        soil_url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lng}&lat={lat}&property=bdod&property=cec&property=cfvo&property=clay&property=nitrogen&property=ocd&property=ocs&property=phh2o&property=sand&property=silt&property=soc&property=wv0010&property=wv0033&property=wv1500&depth=15-30cm&value=Q0.05&value=Q0.5&value=Q0.95&value=mean&value=uncertainty"
        soil_response = requests.get(soil_url)
        soil_response.raise_for_status()
        soil_data = soil_response.json()

        # 2. Call Weather API (requires key)
        weather_url = f"https://history.openweathermap.org/data/2.5/aggregated/year?lat={lat}&lon={lng}&appid={WEATHER_API_KEY}"
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        return jsonify({
            'inputs': data,
            'soilData': soil_data,
            'weatherData': weather_data
        })

    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
