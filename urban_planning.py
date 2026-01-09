import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import random

# --- Configuration ---
# In a real app, this would come from a config file or environment variables
ZURICH_POPULATION_DENSITY_GEOJSON = 'templates/nasa_heat_risk_zone.json'

# --- Green Space Equity Analysis ---

def analyze_green_space_equity():
    """
    Analyzes the distribution of green space relative to population density.
    This is a simulation and uses the NASA heat risk data as a proxy for population density.
    """
    try:
        # Load the GeoJSON which contains population density (proxied by heat risk)
        gdf_population = gpd.read_file(ZURICH_POPULATION_DENSITY_GEOJSON)
        gdf_population = gdf_population.to_crs(epsg=4326) # Ensure standard CRS
    except Exception as e:
        print(f"Error loading GeoJSON: {e}")
        return {
            "error": "Failed to load population data.",
            "zones": []
        }

    # --- Simulate Green Spaces ---
    # In a real scenario, this data would come from a GIS database (e.g., OpenStreetMap, City's GIS data)
    # Here, we generate random "parks" for demonstration.
    green_spaces = []
    for i in range(15): # Generate 15 random small-to-medium parks
        # Center the parks around Zurich's main area
        center_lat, center_lon = 47.37, 8.54
        lat = center_lat + (random.uniform(-0.05, 0.05))
        lon = center_lon + (random.uniform(-0.05, 0.05))
        
        # Create a small polygonal area for the park
        size = random.uniform(0.0005, 0.002)
        poly = Polygon([
            (lon, lat),
            (lon + size, lat),
            (lon + size, lat + size),
            (lon, lat + size)
        ])
        green_spaces.append({
            'id': f'park_{i}',
            'name': f'Simulated Park #{i+1}',
            'geometry': poly
        })

    gdf_parks = gpd.GeoDataFrame(green_spaces, geometry='geometry', crs="EPSG:4326")

    # --- Analysis ---
    analysis_results = []

    for index, zone in gdf_population.iterrows():
        zone_geom = zone.geometry
        
        # Find parks that intersect with the current population zone
        intersecting_parks = gdf_parks[gdf_parks.intersects(zone_geom)]
        
        # Calculate the area of intersection
        green_space_area_in_zone = 0
        if not intersecting_parks.empty:
            # Project to a suitable CRS for area calculation (e.g., UTM zone 32N for Zurich)
            intersection_projected = gpd.overlay(
                intersecting_parks.to_crs(epsg=32632), 
                gpd.GeoDataFrame(geometry=[zone_geom], crs="EPSG:4326").to_crs(epsg=32632), 
                how='intersection'
            )
            green_space_area_in_zone = intersection_projected.area.sum() # Area in square meters

        # --- Equity Score Calculation (Simplified) ---
        # This is a conceptual metric. A real one would be more complex.
        # We'll use population density (proxied by 'risk_level') and green space area.
        
        population_density_score = zone['risk_level'] # Using risk_level (1-5) as a proxy
        
        # Normalize green space area per capita (conceptual)
        # Assume zone area is roughly constant for this simulation
        # A higher score is better (more green space per 'person')
        green_space_score = (green_space_area_in_zone / (population_density_score * 1000)) if population_density_score > 0 else 0

        # Final Equity Score: Lower is worse (high population, low green space)
        # We want to highlight areas where green_space_score is low and population is high.
        equity_score = green_space_score * 10 - population_density_score
        
        if equity_score < 0:
            equity_rating = "Very Low"
            recommendation = "Urgent priority. This area is critically underserved with green space relative to its population density. Recommend immediate land acquisition for new parks, development of community gardens, and greening of public spaces."
        elif equity_score < 5:
            equity_rating = "Low"
            recommendation = "High priority. Consider incentives for green roofs, converting vacant lots to 'pocket parks', and planting street trees to improve local green coverage."
        elif equity_score < 15:
            equity_rating = "Moderate"
            recommendation = "Monitor. While not critical, opportunities to enhance existing parks or add small green installations should be explored in future planning cycles."
        else:
            equity_rating = "Good"
            recommendation = "Well-served. This area has a healthy ratio of green space to population. Focus on maintenance and biodiversity enhancement of existing parks."

        analysis_results.append({
            "zone_id": zone['id'],
            "population_density_proxy": population_density_score,
            "green_space_area_sqm": round(green_space_area_in_zone),
            "equity_rating": equity_rating,
            "recommendation": recommendation,
            "geometry": zone_geom.__geo_interface__
        })

    return {
        "zones": analysis_results,
        "parks": gdf_parks.__geo_interface__
    }

# --- Previous Green Space Functions (for compatibility) ---

ZURICH_GREEN_SPACES = [
    {"id": "rieterpark", "name": "Rieterpark", "lat": 47.3553, "lon": 8.5302},
    {"id": "platzspitz", "name": "Platzspitz", "lat": 47.3797, "lon": 8.5399},
    {"id": "belvoirpark", "name": "Belvoirpark", "lat": 47.3584, "lon": 8.5342},
    {"id": "irchelpark", "name": "Irchelpark", "lat": 47.3963, "lon": 8.5493},
    {"id": "josefwiese", "name": "Josefwiese", "lat": 47.3868, "lon": 8.5183},
    {"id": "chinagarten", "name": "Chinagarten Zürich", "lat": 47.3588, "lon": 8.5524},
    {"id": "lindenhof", "name": "Lindenhof", "lat": 47.3725, "lon": 8.5413},
    {"id": "botanischer_garten", "name": "Old Botanical Garden", "lat": 47.3689, "lon": 8.5335},
]

def get_green_spaces():
    """
    Returns the list of green spaces as a simple JSON object.
    """
    return ZURICH_GREEN_SPACES

def calculate_service_areas(walking_distance_meters):
    """
    Calculates the service area (as a circular buffer) for each green space.
    """
    from shapely.geometry import Point, mapping
    features = []
    
    lat_degree_in_meters = 111100
    lon_degree_in_meters = 75600

    for space in ZURICH_GREEN_SPACES:
        center_point = Point(space['lon'], space['lat'])
        
        buffer_lat = walking_distance_meters / lat_degree_in_meters
        buffer_lon = walking_distance_meters / lon_degree_in_meters
        
        buffer = center_point.buffer(max(buffer_lat, buffer_lon), resolution=16)

        feature = {
            "type": "Feature",
            "geometry": mapping(buffer),
            "properties": {
                "name": space["name"]
            }
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }


if __name__ == '__main__':
    # For direct testing of the module
    results = analyze_green_space_equity()
    if "error" in results:
        print(results["error"])
    else:
        print(f"Successfully analyzed {len(results['zones'])} zones.")
        
        # Print a summary for a few zones
        for zone in results['zones'][:3]:
            print(f"\n--- Zone ID: {zone['zone_id']} ---")
            print(f"  Equity Rating: {zone['equity_rating']}")
            print(f"  Population Density (Proxy): {zone['population_density_proxy']}/5")
            print(f"  Green Space Area: {zone['green_space_area_sqm']} m²")
            print(f"  Recommendation: {zone['recommendation']}")
