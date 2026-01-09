import StreetNetwork as sn
import networkx as nx
import osmnx as ox
from typing import List, Tuple
import matplotlib.pyplot as plt
import simulation as sim       
import matplotlib.lines as mlines
from shapely.geometry import Polygon
import folium
from folium.plugins import MarkerCluster 
from typing import List, Tuple, Dict
from pyproj import Transformer, transform 

def composite_cost_function(u, v, data, alpha: float):
    length_cost = data.get('length', 0)
    crowding_cost = data.get('crowding_level', 0) #default crowding level is 1 if not exist
    total_cost = (alpha * length_cost) + ((1 - alpha) * 100 * crowding_cost)
    if total_cost < 0:
        return 0
    return total_cost

def calculate_shortest_path_composite(G: nx.MultiDiGraph, orig_node: int, target_node: int, alpha:float) -> Tuple[List, float]:
    #print(f"\n--Processor: Calculating composite cost shortest path (Alpha = {alpha:.2f})...)")
    path_type = "Shortest route(length)" if alpha == 1.0 else "Comfort route(crowding)"
    print(f"\n--Calculating {path_type} (Alpha = {alpha:.2f})...")
    #below weigh_func is for the second method calculating shortest path algorithm
    weight_func = lambda u, v, data: composite_cost_function(u, v, data, alpha = alpha)
    route = ox.shortest_path(G, orig_node, target_node, weight=weight_func)
    if route is None:
        raise Exception(f"No path found for alpha= {alpha:.2f}.")

    #there are two calculate methods if the first way is not the best
    #total_composite_cost = sum(composite_cost_function(u, v, G.get_edge_data(u, v, 0), alpha =alpha) for u, v in zip(route[:-1], route[1:]))
    total_composite_cost = nx.classes.function.path_weight(G, route, weight  = weight_func)
    print(f"Path calcuated. Total Composite Cost: {total_composite_cost: .2f}")
    return route, total_composite_cost

def plot_composite_route(G: nx.MultiDiGraph, route: List, filename: str, cost:float, block_polygon: Dict[str, List[Tuple[float, float]]] = None, start_name: str = "start", end_name: str = "End"):
    print("\n---Visualizing the final composite path and blockade...")
    #define start point
    start_node_id = route[0]
    start_lat = G.nodes[start_node_id]['y'] #纬度
    start_lon = G.nodes[start_node_id]['x'] #经度
    transformer = Transformer.from_crs("epsg:32632", "epsg:4326", always_xy=True)
    start_lon, start_lat = transformer.transform(start_lon, start_lat)
    print(f'start_lat:{start_lat}')
    
    m = folium.Map(location=[start_lat, start_lon], zoom_start=14) #tiles = 'CartoDB Positron')
    #get tha lat and lon
    route_coords = [transformer.transform(G.nodes[n]['x'], G.nodes[n]['y']) for n in route]
    folium.PolyLine(locations = route_coords, color="blue", weight=2.5, opacity=1, tooltip = "Shortest Path").add_to(m)
    print("Route plotted on the map.")

    #plot blockade area if any
    if block_polygon:
        for name, coords in block_polygon.items():
        #lon_lat = [(lon, lat) for lat, lon in block_polygon] #change to shapely polygon object
        #polygon = Polygon(lon_lat)
        #plot polygon and set up facecolor and alha for transparency
            folium.Polygon(
                locations = coords,
                color = '#800000',
                weight = 2,
                fill = True,
                fill_color = '#ff0000',
                fill_opacity = 0.3,
                tooltip = f"Blockade Zone (Alpha = {G.ALPHA:.2f})"
                ).add_to(m)
        print("Blockade area plotted on the map.")
        
        #from version without folium: x, y = polygon.exterior.xy
        #from versio witout folium: ax.fill(x, y, facecolor = 'red', edgecolor = 'black', alpha = 0.3, zorder = 2)
    end_node_id = route[-1]
    end_lat = G.nodes[end_node_id]['y'] 
    end_lon = G.nodes[end_node_id]['x']
    end_lon, end_lat = transformer.transform(end_lon, end_lat)

    folium.Marker(
        location=[start_lat, start_lon], 
        popup= f"Start({start_name})\nCost: {cost:.2f} ",
        icon=folium.Icon(color='blue', icon='play')
        ).add_to(m)
    folium.Marker(
        location=[end_lat, end_lon], 
        popup= f"End({end_name})",
        icon=folium.Icon(color='red', icon='stop')
        ).add_to(m)
    #save the map as HTML
    html_filename = filename.reCplace('.png', '.html')
    m.save(html_filename)
    print(f"Map with composite cost shortest path saved as '{html_filename}'")
    m
    #fig.savefig(filename, dpi=300, bbox_inches='tight')
    
def run_analysis():
    place = "Zurich, Switzerland"
    #orig_lat, orig_lon = 47.3777, 8.544#start point: HB
    #target_lat, target_lon = 47.367, 8.541 #end point: Sechslautenplatz
    ALPHA = 0.5

    #get the user input
    start_name = input("Enter the start location name (e.g., Hauptbahnhof):")
    end_name = input("Enter the end location name (e.g., Sechselautenplatz):")
    try:
        orig_lat, orig_lon = ox.geocode(f"{start_name}, {place}")
        target_lat, target_lon = ox.geocode(f"{end_name}, {place}")
    except Exception as e:
        print(f"Error in geocoding: {e}")
    print(f"Start coordinates: ({orig_lat}, {orig_lon})")
    print(f"End coordinates: ({target_lat}, {target_lon})")
    #find nodes
    G = sn.load_zurich_walk_network(place)
    #sn.plot_and_save_network(G, filename = "zurih_walk_network_encapsulated.png")
    G.ALPHA = ALPHA
    orig_node, target_node = sn.find_nearest_nodes(G, orig_lat, orig_lon, target_lat, target_lon)
    
    print(f"Start node ID(Central): {orig_node}")
    print(f"End node ID(Burklipltaz): {target_node}")
    #Graph pre process(crowding / block)
    G_modified = G.copy()
    G_modified = sim.add_crowding_attribute(G_modified)
    blockades_dict = sim.define_zurich_blockades()
    G_modified = sim.simulate_and_apply_blockades_polygon(G_modified, blockades_dict)    
    G_modified.ALPHA = ALPHA
    #caculate route
    route_composite, cost_composite = calculate_shortest_path_composite(G_modified, orig_node, target_node, alpha = ALPHA)
    #plot shortest route
    plot_composite_route(G_modified, route_composite, filename = "Zurich_composite_path.html", cost = cost_composite, block_polygon = blockades_dict, start_name = start_name, end_name = end_name)
    return G_modified, orig_node, target_node, ALPHA

if __name__ == "__main__":
    run_analysis()
