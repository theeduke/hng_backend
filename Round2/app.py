from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

GEOIP_API_KEY = os.getenv('GEOIP_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

@app.route('/api/hello/', methods=['GET'])
def hello():    
    visitor_name = request.args.get('visitor_name')
    print(request.args.get('visitor_name'))
    if visitor_name:
        visitor_name = visitor_name.strip('"')

    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

#     # Get location from IP address using GeoIP API/ exhausted free tier
    # geoip_url = f'http://api.ipstack.com/{client_ip}?access_key={GEOIP_API_KEY}'
    # geoip_response = requests.get(geoip_url).json()
    # location = geoip_response.get('city','Unknown')
        #using ip-api.com
    geoip_url = f'http://ip-api.com/json/{client_ip}'
    geoip_response = requests.get(geoip_url).json()
    location = geoip_response.get('city')


#     # Get weather data for the location using Weather API
    weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&appid={WEATHER_API_KEY}'
    weather_response = requests.get(weather_url).json()
    temperature = weather_response['main']['temp'] if 'main' in weather_response else 'Unknown'

    greeting = f"Hello, {visitor_name}!, the temperature is {temperature} degrees Celsius in {location}"


    response = {
        "client_ip": client_ip,
        "location": location,
        "greeting": greeting
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

