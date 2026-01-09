import pandas as pd
import re 
import numpy as np 
import random
from datetime import datetime

# --- Configuration for CSV File and Filters ---

FILE_PATH = '2025_verkehrszaehlungen_werte_fussgaenger_velo.csv' 

# Key Counter IDs
TARGET_COUNTER_IDS = [2989, 4255, 2991]

ID_TO_NAME_MAP = {
    2989: 'HB-Passage',
    4255: 'Bellevue-Nadel',
    2991: 'Niederdorf-Brunngasse'
}

# Define the Date Range 
START_DATE_TIME = pd.to_datetime('2025-01-01T00:00')
END_DATE_TIME = pd.to_datetime('2025-01-01T01:00') 

# --- Configuration: Areas of Interest for Crowd Monitoring ---
# These are key public spaces in Zurich that would be monitored.
AREAS_OF_INTEREST = [
    {
        "id": "zurich_hb_main_hall",
        "name": "Zürich HB (Main Hall)",
        "coords": [47.3780, 8.5400],
        "type": "Transport Hub",
        "normal_density": 300, # Expected number of people
    },
    {
        "id": "bellevue_square",
        "name": "Bellevue Square",
        "coords": [47.3662, 8.5448],
        "type": "Public Square",
        "normal_density": 150,
    },
    {
        "id": "paradeplatz",
        "name": "Paradeplatz",
        "coords": [47.3683, 8.5372],
        "type": "Financial District",
        "normal_density": 200,
    },
    {
        "id": "oerlikon_station_square",
        "name": "Oerlikon Station Square",
        "coords": [47.4087, 8.5401],
        "type": "Transport Hub",
        "normal_density": 250,
    },
    {
        "id": "sechselaeutenplatz",
        "name": "Sechseläutenplatz",
        "coords": [47.3655, 8.5470],
        "type": "Event Space",
        "normal_density": 100,
    }
]

# --- Data Loading and Filtering ---

def process_local_crowd_data(file_path, counter_ids, start_dt, end_dt, id_to_name_map):
    """
    Loads data, performs cleaning, time-series resampling (15-min to 1-hour), and final calculation.
    """
    
    print(f"1. Starting to read large CSV file: {file_path}...")
    
    try:
        df = pd.read_csv(
            file_path, 
            parse_dates=['DATUM'],
            sep=',',
            encoding='latin-1' 
        )
        print(f"   --> Successfully loaded {len(df):,} total records.")
        
    except Exception as e:
        print(f"❌ ERROR: An error occurred during loading: {e}")
        return None

    # Rename columns to standard format
    df.rename(columns={
        'FK_STANDORT': 'Counter_ID',
        'DATUM': 'Date_Time'
    }, inplace=True)
    
    # 2. Data Cleaning and Preparation
    
    print("2. Performing data cleaning and time-series aggregation (15-min to 1-hour total)...")
    
    count_cols = ['FUSS_IN', 'FUSS_OUT', 'VELO_IN', 'VELO_OUT']
    
    for col in count_cols:
        if col not in df.columns:
            print(f"❌ ERROR: Required column '{col}' not found in the DataFrame.")
            return None
            
        # Aggressive Regex Cleaning and numeric conversion
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].apply(lambda x: re.sub(r'[^\d.]', '', x))
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # 🔥 CRITICAL FIX: Resample the sub-hourly data into true hourly totals.
    
    # 1. Filter to only the target counter IDs first to reduce processing size
    df_filtered_id = df[df['Counter_ID'].isin(counter_ids)].copy()
    
    # 2. Set the Date_Time column as the index
    df_filtered_id.set_index('Date_Time', inplace=True)
    
    # 3. Group by Counter_ID and then resample the index to Hourly ('H') frequency, summing the counts.
    # This sums the four 15-minute (or sub-hourly) readings into a single hourly total.
    df_hourly = df_filtered_id.groupby('Counter_ID')[count_cols].resample('H').sum().reset_index()

    # 4. Filter the Date Range on the aggregated data
    date_mask = (df_hourly['Date_Time'] >= start_dt) & (df_hourly['Date_Time'] <= end_dt)
    df_final = df_hourly[date_mask].copy()

    # 5. Calculate the final total counts
    df_final['Pedestrian_Count'] = (df_final['FUSS_IN'] + df_final['FUSS_OUT']).astype(int)
    df_final['Bicycle_Count'] = (df_final['VELO_IN'] + df_final['VELO_OUT']).astype(int)
    df_final['Total_Traffic_Count'] = (df_final['Pedestrian_Count'] + df_final['Bicycle_Count']).astype(int)
    
    # 3. Apply Filters (already done in step 1 and 4, just checking status)
    print(f"3. Applying date and Counter ID filters locally...")
    
    if df_final.empty:
        print(f"❌ Warning: Filtering resulted in an empty dataset. Check your dates or the Counter IDs.")
        return None
        
    print(f"   --> Filtered down to {len(df_final):,} records (now 1-hour aggregated).")
    
    # 4. Final Data Selection and Mapping
    
    df_final['Location_Name'] = df_final['Counter_ID'].map(id_to_name_map)
    
    df_final = df_final[[
        'Date_Time', 
        'Location_Name',
        'Counter_ID', 
        'Pedestrian_Count', 
        'Bicycle_Count',
        'Total_Traffic_Count'
    ]].sort_values(by=['Date_Time', 'Location_Name'])
    
    return df_final

# --- Simulation Logic ---

def analyze_crowd_density():
    """
    Simulates a real-time AI analysis of crowd density and behavior
    at predefined Areas of Interest.
    """
    analysis_results = []
    
    for area in AREAS_OF_INTEREST:
        # Simulate a random event
        event_chance = random.random()
        current_time = datetime.now()
        
        # Default state: Normal
        status = "Normal"
        alert_level = "Green"
        current_density = area["normal_density"] + random.randint(-50, 50)
        recommendation = "Crowd density is within expected parameters. Continue routine monitoring."

        # --- Anomaly Simulation ---

        # 1. Overcrowding (e.g., spontaneous protest, event overflow)
        # More likely during peak hours (12-2pm, 5-7pm)
        is_peak_hour = 12 <= current_time.hour <= 14 or 17 <= current_time.hour <= 19
        if event_chance < 0.1 and is_peak_hour:
            status = "Overcrowding Detected"
            alert_level = "Orange"
            current_density *= random.uniform(1.8, 2.5)
            recommendation = "Density exceeds threshold. Monitor for potential crushes. Recommend dispatching ground personnel to manage flow and open alternative exits."

        # 2. Rapid Dispersal (e.g., panic, security threat)
        elif 0.1 <= event_chance < 0.15:
            status = "Rapid Dispersal"
            alert_level = "Red"
            current_density *= random.uniform(0.1, 0.3)
            recommendation = "Sudden, rapid crowd dispersal detected. This is a critical indicator of a potential safety or security threat. IMMEDIATE dispatch of security/emergency services is required. Lock down surrounding areas."

        # 3. Unusual Gathering (e.g., loitering, potential flash mob)
        # More likely during off-peak hours
        elif 0.15 <= event_chance < 0.25 and not is_peak_hour:
            status = "Anomalous Stationary Group"
            alert_level = "Yellow"
            current_density += random.randint(50, 100)
            recommendation = "A large group has remained stationary for an unusual length of time. This could be a precursor to an unauthorized event. Advise remote surveillance and have a patrol unit on standby."

        analysis_results.append({
            "id": area["id"],
            "name": area["name"],
            "coords": area["coords"],
            "status": status,
            "alert_level": alert_level,
            "current_density": int(current_density),
            "normal_density": area["normal_density"],
            "recommendation": recommendation,
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S")
        })

    return analysis_results

# --- Execute the script ---

if __name__ == "__main__":
    print(f"Targeting dates: {START_DATE_TIME.strftime('%Y-%m-%d')} to {END_DATE_TIME.strftime('%Y-%m-%d')}")
    print(f"Targeting Counter IDs (FK_STANDORT): {TARGET_COUNTER_IDS}")
    
    crowd_data = process_local_crowd_data(
        FILE_PATH, TARGET_COUNTER_IDS, 
        START_DATE_TIME, END_DATE_TIME, 
        ID_TO_NAME_MAP
    )

    if crowd_data is not None and not crowd_data.empty:
        non_zero_crowd_data = crowd_data[crowd_data['Total_Traffic_Count'] > 0]
        
        # Confirmation that counts are now non-zero
        if not non_zero_crowd_data.empty:
            print("\n4. Confirming non-zero data in a random sample (1-hour totals):")
            sample = non_zero_crowd_data.sample(min(5, len(non_zero_crowd_data)), random_state=42)
            print(sample[['Date_Time', 'Location_Name', 'Total_Traffic_Count', 'Pedestrian_Count', 'Bicycle_Count']].to_string())
        else:
             print("\n4. Note: Filtered data contains no records with Total_Traffic_Count > 0. The counters were genuinely inactive or recorded only zeros for this specific date range/location.")

        print("\n--- Data successfully loaded, filtered, and processed 🎉 ---")
        # The number of records will now be (Hours in range * 3 locations)
        print(f"Total number of FINAL records (Hourly Totals): {len(crowd_data):,}")
        
        # Final Analysis
        # Note: The 'mean' now gives the average hourly total traffic for the entire period.
        hourly_average = crowd_data.groupby('Location_Name')['Total_Traffic_Count'].mean().sort_values(ascending=False)
        print(f"\n5. Average TOTAL HOURLY TRAFFIC Counts ({START_DATE_TIME.year}) by Location:")
        
        print(hourly_average.map('{:,.0f}'.format).to_string())

        OUTPUT_FILE = 'zurich_hourly_traffic_totals_2025_filtered.csv'
        crowd_data.to_csv(OUTPUT_FILE, index=False)
        print(f"\nData saved to {OUTPUT_FILE}")
    
    results = analyze_crowd_density()
    print("--- Crowd Security Analysis ---")
    for result in results:
        if result['alert_level'] != "Green":
            print(f"\n!!! ALERT at {result['name']} !!!")
            print(f"  Status: {result['status']} (Level: {result['alert_level']})")
            print(f"  Density: {result['current_density']} (Normal: {result['normal_density']})")
            print(f"  Recommendation: {result['recommendation']}")
            print(f"  Timestamp: {result['timestamp']}")
    
    print("\n--- Full System Status ---")
    for result in results:
        print(f"- {result['name']}: {result['status']}")