import requests
import os

# --- CONFIGURATION ---
# IMPORTANT: Replace with your own free OpenWeatherMap API key.
# You can get one here: https://openweathermap.org/appid
WEATHER_API_KEY = "your key" # This is a sample key
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_current_weather(lat=47.3769, lon=8.5417):
    """
    Fetches the current weather for a given latitude and longitude (defaulting to Zurich).

    Returns:
        dict: A dictionary with formatted weather data or None if an error occurs.
    """
    if not WEATHER_API_KEY or WEATHER_API_KEY == "YOUR_OPENWEATHERMAP_API_KEY":
        print("Warning: OpenWeatherMap API key is not set. Weather feature will be disabled.")
        return None

    params = {
        'lat': lat,
        'lon': lon,
        'appid': WEATHER_API_KEY,
        'units': 'metric'  # Get temperature in Celsius
    }

    try:
        response = requests.get(WEATHER_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Format the data into a clean structure
        weather_info = {
            "location": data.get('name', 'Unknown'),
            "temperature": f"{data['main']['temp']:.1f}°C",
            "condition": data['weather'][0]['main'],
            "description": data['weather'][0]['description'].capitalize(),
            "icon": f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
            "wind_speed": f"{data['wind']['speed'] * 3.6:.1f} km/h", # Convert m/s to km/h
            "humidity": f"{data['main']['humidity']}%"
        }
        return weather_info

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Error parsing weather data: {e}")
        return None

