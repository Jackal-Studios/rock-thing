# apicalls.py

from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
import requests
import os

load_dotenv() 
# Create a blueprint for your API calls
apicalls_bp = Blueprint('apicalls', __name__)

# Load your secret API key securely
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

@apicalls_bp.route('/api/get-soil-weather', methods=['POST'])
def get_soil_weather():
    data = request.get_json()
    lat = data.get('latitude')
    lng = data.get('longitude')
    print("balls")
    try:
        print("ballsss")
        # 1. Call Soil API (no key required)
        soil_url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lng}&lat={lat}&property=bdod&property=cec&property=cfvo&property=clay&property=nitrogen&property=ocd&property=ocs&property=phh2o&property=sand&property=silt&property=soc&property=wv0010&property=wv0033&property=wv1500&depth=15-30cm&value=Q0.05&value=Q0.5&value=Q0.95&value=mean&value=uncertainty"
        soil_response = requests.get(soil_url)
        soil_response.raise_for_status()
        soil_data = soil_response.json()

        # 2. Call Weather API (requires key)
        print("ballz")
        weather_url = f"https://history.openweathermap.org/data/2.5/aggregated/year?lat={lat}&lon={lng}&appid={WEATHER_API_KEY}"
        print(WEATHER_API_KEY)
        print("alls")
        weather_response = requests.get(weather_url)
        print("b")
        print("Latitude:", lat, "Longitude:", lng)
        print("Weather API status:", weather_response.status_code)
        print("Weather API response:", weather_response.text)
        weather_response.raise_for_status()
        print("balz")
        weather_data = weather_response.json()
        print("balllls")

        return jsonify({
            'inputs': data,
            'soilData': soil_data,
            'weatherData': weather_data
        })

    except requests.RequestException as e:
        print("errorerdkdlfg")
        return jsonify({'error': str(e)}), 500