import random
from shapely.geometry import Point, LineString
from geopy.distance import great_circle
from typing import Tuple, List, Dict
import networkx as nx
import osmnx as ox


#find the location lon and lat
#lat, lon = ox.geocode("Sechseläutenplatz, Zürich")
#print(f"纬度 (Lat): {lat}, 经度 (Lon): {lon}") 


def define_zurich_blockades() -> Dict[str, List[Tuple[float, float]]]:
    # Define the coordinates of the block polygon in Zurich
    #this block could be modified accoding to Zurich stadt database
    blockades = {
    "HB_Block": [ # Hauptbahnhof (苏黎世中央火车站) 区域
        (47.3789, 8.5392), # 东北角
        (47.3795, 8.5370), # 西北角
        (47.3775, 8.5365), # 西南角
        (47.3769, 8.5387), # 东南角
        (47.3789, 8.5392)  # 闭合点
    ],
    "Sechseläutenplatz_Block": [ 
        (47.3675, 8.5475), # 东北角
        (47.3675, 8.5450), # 西北角
        (47.3660, 8.5450), # 西南角
        (47.3660, 8.5475), # 东南角
        (47.3675, 8.5475)  # 闭合点
    ],
    # 新的 Niederdorf/Brundgasse 区域
    "Niederdorf_Brundgasse_Block": [ 
        (47.3755, 8.5480), # 东北角
        (47.3755, 8.5440), # 西北角
        (47.3725, 8.5440), # 西南角
        (47.3725, 8.5480), # 东南角
        (47.3755, 8.5480)  # 闭合点
    ]
}

    print(f"---simulation: Defined {len(blockades)} custom blockade zones in Zurich.")
    return blockades

def simulate_and_apply_blockades_polygon(G: nx.MultiDiGraph, blockades_dict: Dict[str, List[Tuple[float, float]]]) -> nx.MultiDiGraph:
    # Simulate random blockades within the defined polygon
    G_copy = G.copy()
    #total_removed_edges = 0
    '''''
    for name,block_polygon in blockades_dict.items():
        lon_lat = [(lon, lat) for lat, lon in block_polygon]
        polygon = Polygon(lon_lat)
        gdf_edges = ox.graph_to_gdfs(G_removed, nodes=False, edges=True)
        edges_in_polygon = gdf_edges[gdf_edges.geometry.intersects(polygon)]
        edges_to_remove = [(row['u'], row['v'], row['key']) for index, row in edges_in_polygon.iterrows()]

        G_removed.remove_edges_from(edges_to_remove)
        current_removed_count = len(edges_to_remove) 
        total_removed_edges += current_removed_count
    #print(f"Removed {len(total_removed_edges)} edges acorss all blockade zones.")
    '''
    return G_copy

#simulation the crowding level, could be modified
def add_crowding_attribute(G: nx.MultiDiGraph) -> nx.MultiDiGraph:
    print("\n---Adding crowding attributes to edges...")
    #  Add a 'crowding' attribute to each edge in the graph
    for u, v, key, data in G.edges(keys=True, data=True): #u and v are the nodes, key is the edge key, data is the edge attributes
        # Simulate crowding level as a random integer between 1 and 10
        data['crowding_level'] = random.randint(1, 10)
    return G
## if want to find the crowing level from node u to node v:
#u = 24706594 #example
#v = 85934526 # example
# edge_data = G_modified.get_edge_data(u, v, key=0)
# print(edge_data.get('crowding_level'))
# output might bec：8

def run_simulation(new_route_coords, route_type, existing_intersections, existing_stops):
    """
    Analyzes a proposed new infrastructure route and returns an impact assessment.

    Args:
        new_route_coords (list): A list of [lat, lon] coordinates for the new route.
        route_type (str): 'road', 'bike_lane', or 'pt_route'.
        existing_intersections (dict): Dictionary of existing high-risk intersections.
        existing_stops (dict): Dictionary of existing public transport stops.

    Returns:
        dict: A dictionary containing the simulation report and impact score.
    """
    report = f"### 📈 Scenario Simulation Report: New {route_type.replace('_', ' ').title()}\\n\\n"
    impact_score = 50  # Start with a neutral score

    if not new_route_coords or len(new_route_coords) < 2:
        return {"report": "Error: Invalid route provided for simulation.", "score": 0}

    new_route_line = LineString([(p[1], p[0]) for p in new_route_coords])
    route_length_km = 0
    if len(new_route_coords) > 1:
        for i in range(len(new_route_coords) - 1):
            point1 = (new_route_coords[i][0], new_route_coords[i][1])
            point2 = (new_route_coords[i+1][0], new_route_coords[i+1][1])
            route_length_km += great_circle(point1, point2).km


    # --- Analysis Logic ---

    # 1. Congestion & Safety Impact
    nearby_intersections = 0
    for name, coords in existing_intersections.items():
        intersection_point = Point(coords[1], coords[0])
        # Check if the new route is within ~500 meters of a known problem intersection
        if new_route_line.distance(intersection_point) < 0.005:
            nearby_intersections += 1
    
    if route_type in ['road', 'bike_lane']:
        if nearby_intersections > 0:
            report += f"**⚠️ Safety Concern:** Route passes close to **{nearby_intersections}** known high-risk intersection(s). This could increase accident risk if not properly managed.\\n"
            impact_score -= nearby_intersections * 10
        else:
            report += f"**✅ Safety Analysis:** Route avoids major known high-risk intersections, which is positive.\\n"
            impact_score += 10

    # 2. Public Transport Connectivity
    if route_type == 'pt_route':
        connected_stops = 0
        for name, coords in existing_stops.items():
            stop_point = Point(coords[1], coords[0])
            if new_route_line.distance(stop_point) < 0.002: # within ~200m
                connected_stops += 1
        report += f"**✅ Connectivity Boost:** This new route directly connects or passes near **{connected_stops}** existing transport hubs, potentially creating a more resilient network.\\n"
        impact_score += connected_stops * 5
        report += f"**💡 Recommendation:** Model passenger flow to see if this new {route_length_km:.2f} km link reduces travel time between key residential and commercial zones.\\n"
        impact_score += route_length_km * 2

    # 3. Accessibility & Livability (for Bike Lanes)
    if route_type == 'bike_lane':
        # Simulate proximity to green spaces or residential areas (positive)
        # For this demo, we'll use a random factor.
        livability_factor = random.uniform(0.8, 1.2)
        if livability_factor > 1.0:
            report += f"**✅ Livability Improvement:** This bike lane appears to improve access to residential areas or parks, promoting healthier lifestyles.\\n"
            impact_score += 15
        else:
            report += f"**⚠️ Urban Integration:** The proposed route runs through a dense commercial or industrial area. Ensure cyclist safety with dedicated, protected barriers.\\n"
            impact_score -= 5
        report += f"**💡 Recommendation:** A {route_length_km:.2f} km dedicated bike lane is a significant addition. Ensure it connects to the existing cycling network to maximize utility.\\n"

    # 4. General Road Impact
    if route_type == 'road':
        congestion_factor = random.uniform(0.5, 1.5)
        if congestion_factor > 1.2:
            report += f"**❌ Congestion Risk:** High risk of induced demand. A new {route_length_km:.2f} km road in this area might attract more car traffic, worsening overall congestion.\\n"
            impact_score -= 20
        else:
            report += f"**✅ Congestion Relief:** This route could potentially offload traffic from parallel congested arteries. Further micro-simulation is needed.\\n"
            impact_score += 15
        report += f"**💡 Recommendation:** Analyze the land use zoning around the proposed road. If it encourages more driving, consider implementing tolls or pairing it with new public transport options.\\n"

    # --- Final Score & Summary ---
    impact_score = max(0, min(100, int(impact_score)))
    
    if impact_score > 75:
        summary = "Highly Recommended"
        color = "green"
    elif impact_score > 50:
        summary = "Potentially Viable"
        color = "orange"
    else:
        summary = "Requires Re-evaluation"
        color = "red"

    final_report = {
        "report": report,
        "score": impact_score,
        "summary": summary,
        "color": color
    }
    return final_report
