# Urban Intelligence & Sustainability Platform

This project is a comprehensive web-based platform designed for urban planners and citizens to monitor, analyze, and interact with city-wide data. It leverages real-time (and simulated) data to provide insights into traffic congestion, public transport efficiency, environmental risks, and citizen well-being. The platform is built with a Flask backend and a dynamic, map-centric frontend.

## ✨ Features

The platform is divided into two main portals: one for city planners and one for citizens.

### 🏙️ For Urban Planners (`/planner`)

-   **Real-Time Dashboard**: Visualizes key urban metrics on an interactive map.
    -   **PT Delay Hotspots**: Monitors and ranks public transport stops by delay severity.
    -   **Congestion Heatmap**: Displays real-time traffic congestion levels across the city.
-   **Route Adherence Analysis**: Tracks the performance of specific public transport lines (e.g., Tram Line 11) against their schedules.
-   **Pedestrian Safety**: Identifies high-risk intersections for pedestrians and recommends safety interventions.
-   **AI Urban Mentor**: Provides AI-driven strategic advice and budget allocation recommendations based on the most critical urban issues.
-   **Dynamic Rerouting**: Simulates the use of real-time satellite/aerial imagery to detect unexpected events (like crowd surges) and suggests dynamic rerouting for traffic and public transport.
-   **Green Space Equity**: Analyzes the accessibility of parks and green spaces for residents to ensure equitable distribution.
-   **Environmental Hazard Planning**: Maps and assesses risks from environmental hazards like landslides.
-   **Scenario Simulation**: Allows planners to simulate the effects of road closures or other events on the city's traffic network.

### 🚶 For Citizens (`/citizen`)

-   **Heat-Stress Aware Routing**: A user-facing tool that provides walking or cycling routes that actively avoid high-temperature zones, based on a concept using NASA's Land Surface Temperature (LST) data.
-   **Smart Navigation**: A Google Maps-powered navigation tool that provides optimal routes for driving, walking, cycling, or transit, taking into account real-time traffic.
-   **Construction Rerouting**: Helps users navigate around known construction zones.
-   **Event Discovery**: Lists current events happening in the city.
-   **Event Visit Planner**: Helps users plan their visit to events (like Christmas markets) by suggesting less crowded options and calculating the best route and departure time.

## 🛠️ Technology Stack

-   **Backend**: Python with **Flask**
-   **Frontend**: HTML, CSS, JavaScript
-   **Mapping**: **Leaflet.js** for interactive maps
-   **Routing & Geocoding**: **Google Maps Platform APIs** (Directions, Places, Street View)
-   **Core Python Libraries**:
    -   `pandas`: For data manipulation.
    -   `requests`: For making API calls.
    -   `googlemaps` & `polyline`: For Google Maps integration.
    -   `geopy` & `shapely`: For geospatial calculations.
-   **Data Formats**: GeoJSON, JSON, CSV

## ⚙️ Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Keys:**
    Open `app.py` and replace the placeholder for the `GOOGLE_API_KEY` with your own Google Maps Platform API key.
    ```python
    # app.py
    GOOGLE_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"
    ```

## 🚀 How to Run the Application

With your virtual environment activated and dependencies installed, run the Flask application from the root directory:

```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`.

-   **Main Portal**: `http://127.0.0.1:5000/`
-   **Planner Dashboard**: `http://127.0.0.1:5000/planner`
-   **Citizen Portal**: `http://127.0.0.1:5000/citizen`



## 🎥 Dashboard Previews

Below are video previews demonstrating the dashboards for both Urban Planners and Users. The videos are hosted on Google Drive for easy access:

### 🏙️ Urban Planner Dashboard

[Urban Planner Dashboard (Google Drive)](https://drive.google.com/file/d/1aX6iNYqISWLHym_3o6MURwPs_M6QJhlx/view?usp=sharing)

### 🚶 User Dashboard

[User Dashboard (Google Drive)](https://drive.google.com/file/d/1ioxpv4mgqwU0xiDX63MupFobJB9kpO03/view?usp=sharings)

## 📁 Project Structure

```
.
├── app.py                  # Main Flask application with all routes and logic
├── requirements.txt        # Python dependencies
├── templates/              # HTML files for the frontend
│   ├── index.html          # Main planner dashboard
│   ├── home.html           # Main landing page
│   ├── citizen.html        # Citizen portal
│   ├── planner.html        # Planner portal
│   ├── construction.html   # Construction routing page
│   ├── navigation.html     # General navigation page
│   ├── user_routing_map.html # Heat-stress routing page
│   └── ...                 # Other feature pages
├── static/                 # CSS stylesheets
│   └── *.css
├── *.py                    # Python modules for specific features (currently mocked in app.py)
└── *.csv                   # Data files
```

## 🌐 API Endpoints

The application exposes several API endpoints that are consumed by the frontend. Most of these endpoints provide simulated data for demonstration purposes.

-   `/api/analyze`: Provides public transport delay hotspot data.
-   `/api/route_adherence`: Data for tram line route adherence.
-   `/api/pedestrian_risk`: Pedestrian safety risk scores for intersections.
-   `/api/mentor_advice`: AI-generated report for planners.
-   `/api/congestion-heatmap`: Data for the traffic congestion map.
-   `/api/live-events`: Information on current city events.
-   `/api/smart-route`: **(Live)** Google Maps-powered routing for navigation.
-   `/api/user-route`: Calculates a route avoiding heat-stress zones.
-   ... and many more.


---




