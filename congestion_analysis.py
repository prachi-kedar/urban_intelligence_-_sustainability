import pandas as pd
import random
from datetime import datetime
import requests

# URL for real-time traffic data from Zurich's Open Data Portal
TRAFFIC_DATA_URL = "https://www.ogd.stadt-zuerich.ch/wfs/geoportal/Verkehrszaehlung_Messwerte_Oeff?service=WFS&version=2.0.0&request=GetFeature&outputFormat=GeoJSON&typeName=adm_vzo_messwert_v"

def load_traffic_data():
    """
    Loads and processes real-time traffic data from Zurich's Open Data Portal.
    """
    try:
        response = requests.get(TRAFFIC_DATA_URL, timeout=15)
        response.raise_for_status()
        data = response.json()

        features = data.get('features', [])
        if not features:
            print("Warning: Real-time traffic data feed is empty.")
            return None

        # Extract properties and geometry
        records = []
        for f in features:
            props = f['properties']
            geom = f.get('geometry')
            if geom and geom['type'] == 'Point':
                # GeoJSON is [lon, lat]
                props['lon'], props['lat'] = geom['coordinates']
                records.append(props)

        df = pd.DataFrame(records)

        # Basic data cleaning and preparation
        df['messwert'] = pd.to_numeric(df['messwert'], errors='coerce')
        df.dropna(subset=['messwert', 'lat', 'lon'], inplace=True)
        df['zeitpunkt'] = pd.to_datetime(df['zeitpunkt'])

        return df

    except requests.exceptions.RequestException as e:
        print(f"Error fetching real-time traffic data: {e}")
        return None
    except Exception as e:
        print(f"Error processing traffic data: {e}")
        return None


def simulate_satellite_view():
    """
    Simulates analysis from satellite imagery (e.g., Sentinel/Copernicus).
    In a real scenario, this would involve a pipeline that fetches images,
    runs an object detection model to count vehicles, and calculates road occupancy.

    Here, we'll simulate this by identifying a few "hotspots" that
    the satellite "sees" as congested.
    """
    # These are known busy areas in Zurich we can use for simulation.
    hotspots = {
        "Hardbrücke_Satellite": (47.3828, 8.5135),
        "Rosengartenstrasse_Satellite": (47.3900, 8.5250),
        "Escher-Wyss-Platz_Satellite": (47.3912, 8.5145),
        "Bellevue_Satellite": (47.3662, 8.5448),
    }

    satellite_congestion_points = []
    for name, (lat, lon) in hotspots.items():
        # Simulate a high congestion score for these satellite-detected hotspots.
        # Add some randomness to the location to make the heatmap more dynamic.
        for _ in range(10): # Add more points around the hotspot
            satellite_congestion_points.append({
                'lat': lat + random.uniform(-0.001, 0.001),
                'lon': lon + random.uniform(-0.001, 0.001),
                'intensity': random.uniform(0.8, 1.0) # High intensity
            })
            
    return satellite_congestion_points

def generate_congestion_heatmap_data(traffic_df):
    """
    Combines Zurich open data with simulated satellite views to create a heatmap.
    
    Args:
        traffic_df (pd.DataFrame): DataFrame from `load_traffic_data`.

    Returns:
        list: A list of [lat, lon, intensity] for the heatmap.
    """
    heatmap_data = []

    # 1. Process Real-Time Zurich Open Data
    if traffic_df is not None and not traffic_df.empty:
        # Normalize the 'messwert' (measurement value) to get an intensity score.
        # Different sensors have different max values, so we'll cap at a reasonable number
        # for visualization purposes, e.g., 1500 vehicles/hour.
        max_volume = 1500 
        traffic_df['intensity'] = traffic_df['messwert'] / max_volume
        traffic_df['intensity'] = traffic_df['intensity'].clip(0, 1) # Ensure intensity is between 0 and 1

        for _, row in traffic_df.iterrows():
            # The new load_traffic_data function already extracts lat and lon
            heatmap_data.append([row['lat'], row['lon'], row['intensity']])

    # 2. Add Simulated Satellite Data (as before)
    satellite_points = simulate_satellite_view()
    for point in satellite_points:
        heatmap_data.append([point['lat'], point['lon'], point['intensity']])
        
    # 3. Add some general "background" congestion (as before)
    for _ in range(50):
        lat = random.uniform(47.36, 47.39)
        lon = random.uniform(8.52, 8.56)
        intensity = random.uniform(0.1, 0.3)
        heatmap_data.append([lat, lon, intensity])

    return heatmap_data
