import requests
import os

# It's good practice to use the same API key as the weather module.
# You can store it in an environment variable for better security.
API_KEY = os.environ.get("OPENWEATHER_API_KEY", "YOUR_DEFAULT_API_KEY") # Use the same key as in weather.py
BASE_URL = "http://api.openweathermap.org/data/2.5/air_pollution"

# Coordinates for Zurich
ZURICH_LAT = 47.3769
ZURICH_LON = 8.5417

def get_air_quality():
    """
    Fetches air quality data for Zurich from OpenWeatherMap.
    """
    params = {
        "lat": ZURICH_LAT,
        "lon": ZURICH_LON,
        "appid": API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        if data and 'list' in data and data['list']:
            aq_data = data['list'][0]
            aqi = aq_data['main']['aqi']
            components = aq_data['components']

            # Map AQI to a human-readable quality level
            aqi_map = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
            quality = aqi_map.get(aqi, "Unknown")

            return {
                "aqi": aqi,
                "quality": quality,
                "components": {
                    "co": components.get('co'),
                    "no2": components.get('no2'),
                    "o3": components.get('o3'),
                    "pm2_5": components.get('pm2_5'),
                }
            }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching air quality data: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred in get_air_quality: {e}")
        return None

if __name__ == '__main__':
    # For testing the module directly
    # Make sure to set your OpenWeatherMap API key as an environment variable
    # or replace "YOUR_DEFAULT_API_KEY" with your actual key.
    # Note: The key from weather.py should be used here.
    
    # Temporarily set key for direct script run if not in env
    if API_KEY == "YOUR_DEFAULT_API_KEY":
        # This is a placeholder. In a real scenario, use environment variables.
        # You would need to paste your actual key here to test this script directly.
        print("Please set the OPENWEATHER_API_KEY environment variable or replace the placeholder.")
    else:
        air_quality_data = get_air_quality()
        if air_quality_data:
            print("Successfully fetched Air Quality Data for Zurich:")
            print(f"  AQI: {air_quality_data['aqi']} ({air_quality_data['quality']})")
            print("  Components (μg/m³):")
            print(f"    - PM2.5: {air_quality_data['components']['pm2_5']}")
            print(f"    - NO₂: {air_quality_data['components']['no2']}")
            print(f"    - O₃: {air_quality_data['components']['o3']}")
            print(f"    - CO: {air_quality_data['components']['co']}")
        else:
            print("Failed to fetch air quality data.")
