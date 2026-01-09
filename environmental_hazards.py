import random

# --- Simulated Data for Environmental Hazards ---
# This data is for demonstration purposes to simulate risk zones in Zurich.

# Polygons representing areas with steep slopes, potentially prone to landslides.
LANDSLIDE_RISK_ZONES = [
    {
        "id": "zuerichberg_west",
        "name": "Zürichberg - West Slope",
        "risk_level": "High",
        "polygon": [
            [47.383, 8.555],
            [47.380, 8.565],
            [47.375, 8.560],
            [47.378, 8.550]
        ],
        "analysis": "Steep, unconsolidated soil with significant water runoff from the upper forest.",
        "solutions": [
            {"title": "Bio-Engineering", "desc": "Introduce deep-rooted native vegetation (e.g., Hazel, Blackthorn) to stabilize soil layers."},
            {"title": "Retaining Walls", "desc": "Implement terraced retaining walls using locally sourced, permeable materials."},
            {"title": "Improved Drainage", "desc": "Install a subsurface drainage system to reduce soil saturation and hydrostatic pressure."},
            {"title": "Policy", "desc": "Update zoning to restrict new construction in the immediate vicinity without extensive geotechnical surveys."}
        ]
    },
    {
        "id": "uetliberg_north",
        "name": "Uetliberg - North Face",
        "risk_level": "Moderate",
        "polygon": [
            [47.355, 8.490],
            [47.352, 8.498],
            [47.348, 8.495],
            [47.351, 8.488]
        ],
        "analysis": "Stable bedrock but with loose surface material; risk increases after heavy rainfall.",
        "solutions": [
            {"title": "Erosion Control", "desc": "Utilize erosion control blankets made from biodegradable coconut fiber on exposed surfaces."},
            {"title": "Monitoring", "desc": "Install ground movement sensors to provide early warnings of any soil creep or instability."},
            {"title": "Water Management", "desc": "Construct check dams in runoff channels to slow water velocity and trap sediment."}
        ]
    }
]

# Polylines representing steep road segments that are hazardous in winter.
WINTER_HAZARD_ROADS = [
    {
        "id": "wonnebergstrasse",
        "name": "Wonnebergstrasse",
        "risk_level": "High",
        "path": [
            [47.363, 8.561],
            [47.365, 8.564],
            [47.366, 8.568]
        ],
        "analysis": "A steep gradient (avg. 12%) with sharp turns, receiving little direct sunlight in winter.",
        "solutions": [
            {"title": "Permeable Heated Pavement", "desc": "Install a hydronic or electric heated pavement system using permeable asphalt to prevent ice formation and manage meltwater sustainably."},
            {"title": "High-Traction Surfacing", "desc": "Apply a high-friction surface treatment to increase grip for vehicles and pedestrians."},
            {"title": "Priority Servicing", "desc": "Designate as a 'Priority 1' route for salt/grit spreading, serviced before and during snowfall events."},
            {"title": "Smart Signage", "desc": "Install dynamic LED signs that activate based on temperature sensors to warn drivers of icy conditions."}
        ]
    },
    {
        "id": "germanistrasse",
        "name": "Germanistrasse",
        "risk_level": "Moderate",
        "path": [
            [47.384, 8.558],
            [47.386, 8.562]
        ],
        "analysis": "A straight but consistently steep road, often used as a shortcut.",
        "solutions": [
            {"title": "Eco-Friendly De-icing", "desc": "Mandate the use of calcium magnesium acetate instead of traditional salt to protect surrounding vegetation."},
            {"title": "Traffic Calming", "desc": "Introduce chicanes or speed humps to force lower speeds, reducing the risk of skidding."},
            {"title": "Community Salt Bins", "desc": "Place community grit/salt bins at the top and bottom for residents to use for self-service on sidewalks."}
        ]
    }
]

def get_hazard_data(hazard_type):
    """
    Returns the simulated data for a given hazard type.
    """
    if hazard_type == 'landslide':
        return LANDSLIDE_RISK_ZONES
    elif hazard_type == 'winter':
        return WINTER_HAZARD_ROADS
    else:
        return []

if __name__ == '__main__':
    # Example of how to access the data
    landslide_data = get_hazard_data('landslide')
    print("--- Landslide Risks ---")
    for zone in landslide_data:
        print(f"Zone: {zone['name']} (Risk: {zone['risk_level']})")
        for solution in zone['solutions']:
            print(f"  - {solution['title']}: {solution['desc']}")

    winter_data = get_hazard_data('winter')
    print("\n--- Winter Road Risks ---")
    for road in winter_data:
        print(f"Road: {road['name']} (Risk: {road['risk_level']})")
        for solution in road['solutions']:
            print(f"  - {solution['title']}: {solution['desc']}")
