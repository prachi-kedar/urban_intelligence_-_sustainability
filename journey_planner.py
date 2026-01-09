import os
import io
import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import xgboost as xgb
from math import radians, cos, sin, asin, sqrt
from pandas.errors import ParserError
import chardet
import glob # Added glob for easily handling lists of files

# -------------------------
# USER: input LOCAL file paths
# NOTE: Ensure these files are in the same directory as this script 
# or use the full path.
# -----------------------------------------

# 1. Local path for the station metadata (the one that keeps failing parsing)
STATION_FILE_PATH = "dav.tbl_standort_zaehlung_miv_p.csv" 

# 2. Local paths for the hourly count data (renamed for clarity)
# **NOTE: Use the actual file extensions (e.g., .csv, .txt)**
OD2031_PATH = "sid_dav_verkehrszaehlung_miv_od2031_2025 (1).csv" 
UGZ_PATH = "ugz_ogd_traffic_h1_2023 (1).csv"

# List of all count files to process
COUNT_FILE_PATHS = [
    OD2031_PATH, 
    UGZ_PATH
]
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# DATA LOADING FUNCTIONS
# ----------------------------------------------------------------------

# Helper function for aggressive local CSV parsing (now used for all files)
def load_local_csv_df(file_path):
    """
    Loads data from a local CSV file path, aggressively trying different 
    delimiters and encoding to handle common parsing issues.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    print("Loading local file with aggressive parsing:", file_path)
    
    # 1. Detect encoding once
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    # Use a backup encoding 'latin-1' if chardet returns None, common for OGD data
    encoding = chardet.detect(raw_data)['encoding'] or 'latin-1' 

    # List of separators to try
    separators = [',', ';', '\t'] 
    common_args = {
        'encoding': encoding,
        'comment': '#',       
        'skip_blank_lines': True,
        'on_bad_lines': 'warn',
        'low_memory': False
    }

    # 2. Try simple separators
    for sep in separators:
        try:
            df = pd.read_csv(file_path, sep=sep, **common_args)
            # A good check: if the file has multiple columns, it likely succeeded
            if len(df.columns) > 1 and len(df) > 0:
                print(f"Success with simple separator: '{sep}'")
                return df
        except Exception:
            continue # Try next separator

    # 3. Final Fallback: Aggressive regex separator (e.g., for non-standard quoting)
    print("Trying aggressive regex/quoting fallback...")
    
    try:
        # Regex: comma, zero or more whitespace, optional quote
        df = pd.read_csv(file_path, sep=r',\s*\"?', engine='python', **common_args)
        if len(df.columns) > 1 and len(df) > 0:
            print("Success with regex separator.")
            return df
    except Exception as e_complex:
        print(f"Regex parsing failed ({e_complex}), trying quoting=3 fallback...")
        
        # Fallback 2: Force quoting=3 (QUOTE_NONE)
        try:
             df = pd.read_csv(file_path, sep=',', quoting=3, **common_args)
             if len(df.columns) > 1 and len(df) > 0:
                 print("Success with quoting=3 fallback.")
                 return df
        except Exception as e_final:
            print(f"Final fallback failed: {e_final}")
            raise # Re-raise the error if all attempts fail

    raise ParserError(f"Could not parse file {file_path} with any known method.")

# -------------------------
# Local station file loading now uses the generic aggressive loader
def load_stations(file_path):
    """Loads station metadata and extracts standardized ID and coordinates."""
    df = load_local_csv_df(file_path)
    
    df.columns = df.columns.str.lower().str.replace('"', '').str.strip() # Remove quotes from headers
    print("Station columns found (normalized):", list(df.columns)[:10])

    # 1. FINAL IDENTIFIERS 
    station_col = 'zsid'
    lon_col = 'ekoord'  
    lat_col = 'nkoord'  
    
    # Fallback/Resilience Check
    if station_col not in df.columns:
        station_col = next((c for c in df.columns if any(k in c for k in ['zaehlstelle', 'msid', 'zstname', 'id', 'nr'])), None)
    if lon_col not in df.columns:
        lon_col = next((c for c in df.columns if any(k in c for k in ['wgs84_e', 'lon', 'easting', 'x', 'koordinate_e'])), None)
    if lat_col not in df.columns:
        lat_col = next((c for c in df.columns if any(k in c for k in ['wgs84_n', 'lat', 'northing', 'y', 'koordinate_n'])), None)
    
    if not station_col or not lon_col or not lat_col:
        raise ValueError(
            f"Could not find required columns for station ID and coordinates. "
            f"Search failed for: ID='{station_col}', Lon='{lon_col}', Lat='{lat_col}'. "
            f"Please verify the headers in your local station CSV."
        )

    # Convert coordinates to numeric
    # NOTE: The coordinates might be Swiss grid (LV95/LV03) which are huge numbers.
    df[lon_col] = pd.to_numeric(df[lon_col], errors='coerce')
    df[lat_col] = pd.to_numeric(df[lat_col], errors='coerce')

    # Normalize and return
    stations = df.rename(columns={station_col: 'station_id', lon_col:'lon', lat_col:'lat'})
    stations = stations.dropna(subset=['lat', 'lon'])
    print(f"✅ Final station metadata has {len(stations)} valid stations.")
    return stations[['station_id', 'lon', 'lat']].drop_duplicates(subset=['station_id'])


def load_counts(file_paths):
    """Loads, concatenates, and normalizes hourly traffic count data from local files."""
    dfs = []
    for fp in file_paths:
        df = load_local_csv_df(fp) # Use the aggressive local loader
        dfs.append(df)
    data = pd.concat(dfs, ignore_index=True)
    
    data.columns = data.columns.str.lower()
    print("Counts columns found (normalized):", list(data.columns)[:20])
    
    # 1. Datetime column: Datum (UGZ) or zeitintervall_start (SID)
    dt_cols = ['datum', 'zeitintervall_start', 'timestamp', 'messpunkt_datum']
    dt_col = next((c for c in dt_cols if c in data.columns), None)
    if dt_col is None:
        raise ValueError("Couldn't find a recognized datetime column.")
    
    data = data.rename(columns={dt_col: 'ts'})
    data['ts'] = pd.to_datetime(data['ts'], utc=False, infer_datetime_format=True, errors='coerce')
    data = data.dropna(subset=['ts'])
    
    # 2. Station ID column: standort (UGZ) or msid/zsid (SID)
    station_cols = ['standort', 'msid', 'zsid', 'zsname', 'zaehlstelleid']
    station_col = next((c for c in station_cols if c in data.columns), None)
    
    if station_col is None:
        data['station_id'] = 'DEFAULT_SINGLE_SITE'
    else:
        data = data.rename(columns={station_col: 'station_id'})
    
    # 3. Count column: anzahl (UGZ) or anffahrzeugetotal (SID)
    count_cols = ['anzahl', 'anffahrzeugetotal', 'total', 'miv_total', 'count', 'wert']
    count_col = next((c for c in count_cols if c in data.columns), None)
    
    if count_col is None:
        raise ValueError("Couldn't find a recognized count column.")
    
    data = data.rename(columns={count_col: 'count'})
    
    # 4. Convert count to numeric (handling commas/dots for decimals)
    data['count'] = pd.to_numeric(
        data['count'].astype(str).str.replace(',', '.', regex=False), 
        errors='coerce'
    )
    data = data.dropna(subset=['count'])
    
    # 5. Aggregate: Sum counts per station per hour
    if 'klasse.id' in data.columns:
        print("Aggregating counts across vehicle classes...")
    
    norm = data.groupby(['station_id', pd.Grouper(key='ts', freq='H')])['count'].sum().reset_index()

    print(f"✅ Final normalized counts dataset has {len(norm)} rows.")
    return norm

# ----------------------------------------------------------------------
# FEATURE ENGINEERING, MODELING, AND PLANNING FUNCTIONS (Unchanged from logic)
# ----------------------------------------------------------------------
# [make_features, train_xgb, predict_counts, haversine, find_nearest_station, 
# counts_to_travel_time_base, plan_journey functions remain as provided]
def make_features(df):
    df = df.copy()
    df['hour'] = df['ts'].dt.hour
    df['dow'] = df['ts'].dt.weekday  
    df['hour_sin'] = np.sin(2*np.pi*df['hour']/24)
    df['hour_cos'] = np.cos(2*np.pi*df['hour']/24)
    df['dow_sin'] = np.sin(2*np.pi*df['dow']/7)
    df['dow_cos'] = np.cos(2*np.pi*df['dow']/7)
    df = df.sort_values(['station_id','ts'])
    def get_rolling_mean(series, window):
        return series.shift(1).rolling(window, min_periods=1).mean()
    df['count_lag1'] = df.groupby('station_id')['count'].shift(1).fillna(method='bfill')
    df['count_rolling_3'] = df.groupby('station_id')['count'].transform(lambda x: get_rolling_mean(x, 3))
    df['count_rolling_24'] = df.groupby('station_id')['count'].transform(lambda x: get_rolling_mean(x, 24))
    df = df.dropna(subset=['count_lag1'])
    return df

def train_xgb(df, use_station_feature=True):
    df = df.copy()
    if use_station_feature:
        df['station_id_enc'] = df['station_id'].astype('category').cat.codes
        station_encoder = df.set_index('station_id')['station_id_enc'].drop_duplicates().to_dict()
    else:
        station_encoder = None
    features = ['hour_sin','hour_cos','dow_sin','dow_cos','count_lag1','count_rolling_3','count_rolling_24']
    if use_station_feature:
        features.append('station_id_enc')
    X = df[features]
    y = df['count'].values
    if len(X) < 100:
        return None, features, station_encoder
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, shuffle=False)
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)
    params = {"objective":"reg:squarederror", "eval_metric":"mae", "eta":0.1, "max_depth":6, "subsample":0.8, "seed":42}
    model = xgb.train(params, dtrain, num_boost_round=200, evals=[(dtest,'eval')], early_stopping_rounds=20, verbose_eval=False)
    preds = model.predict(dtest)
    mae = mean_absolute_error(y_test, preds)
    print("XGBoost MAE on test:", mae)
    return model, features, station_encoder

def predict_counts(model, features, station_id, future_ts_list, station_encoder):
    rows = []
    last_count_lag1 = 0 
    last_count_rolling_3 = 0
    last_count_rolling_24 = 0
    for ts in future_ts_list:
        hour = ts.hour
        dow = ts.weekday()
        row = {'hour_sin': np.sin(2*np.pi*hour/24), 'hour_cos': np.cos(2*np.pi*hour/24), 'dow_sin': np.sin(2*np.pi*dow/7), 'dow_cos': np.cos(2*np.pi*dow/7), 'count_lag1': last_count_lag1, 'count_rolling_3': last_count_rolling_3, 'count_rolling_24': last_count_rolling_24}
        if 'station_id_enc' in features:
            row['station_id_enc'] = station_encoder.get(station_id, 0)
        rows.append(row)
    Xf = pd.DataFrame(rows)[features]
    dmat = xgb.DMatrix(Xf)
    return model.predict(dmat)

def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return 6371 * c

def find_nearest_station(stations_df, lat, lon, k=1):
    stations_df = stations_df.copy()
    if 'lat' not in stations_df.columns or 'lon' not in stations_df.columns:
        raise ValueError("Station DataFrame is missing 'lat' or 'lon' columns. Data parsing failed.")
    stations_df['dist_km'] = stations_df.apply(lambda r: haversine(lat, lon, r['lat'], r['lon']), axis=1)
    stations_df = stations_df.sort_values('dist_km')
    return stations_df.head(k)

def counts_to_travel_time_base(count, base_travel_time_min=15.0):
    saturation = 2000.0
    alpha = 1.0
    factor = 1.0 + alpha * (count / saturation)
    return base_travel_time_min * factor

def plan_journey(model, features, stations_df, station_encoder, origin, destination, event_time, arrive_by_minutes=10):
    if model is None:
        return {'error': 'Model training failed due to insufficient or poorly parsed data.'}
    s_o = find_nearest_station(stations_df, origin[0], origin[1], k=1).iloc[0]
    s_d = find_nearest_station(stations_df, destination[0], destination[1], k=1).iloc[0]
    print("Nearest origin station:", s_o.get('name', s_o.get('station_id', 'unknown')), "dist_km", s_o['dist_km'])
    print("Nearest dest station:", s_d.get('name', s_d.get('station_id', 'unknown')), "dist_km", s_d['dist_km'])
    travel_ts = (event_time - timedelta(minutes=counts_to_travel_time_base(0) + arrive_by_minutes)).replace(minute=0, second=0, microsecond=0)
    preds_o = predict_counts(model, features, s_o['station_id'], [travel_ts], station_encoder)
    preds_d = predict_counts(model, features, s_d['station_id'], [travel_ts], station_encoder)
    count_sample = float((preds_o.mean()+preds_d.mean())/2)
    base_travel_time_min = 15.0 
    est_travel_time_min = counts_to_travel_time_base(count_sample, base_travel_time_min=base_travel_time_min)
    recommended_departure = event_time - timedelta(minutes=arrive_by_minutes + est_travel_time_min)
    return {'origin_station': s_o.to_dict(), 'dest_station': s_d.to_dict(), 'predicted_count': count_sample, 'estimated_travel_time_min': est_travel_time_min, 'recommended_departure_time': recommended_departure}


# ----------------------------------------------------------------------
# MAIN EXECUTION
# ----------------------------------------------------------------------

if __name__ == "__main__":
    try:
        # 1) Load data
        stations = load_stations(STATION_FILE_PATH) 
        counts = load_counts(COUNT_FILE_PATHS)

        # 2) Feature engineer
        df_feat = make_features(counts)

        # 3) Train model
        model, features, station_encoder = train_xgb(df_feat, use_station_feature=True)

        # 4) Example journey plan
        origin = (47.3769, 8.5417)
        destination = (47.3745, 8.5480)
        event_time = pd.Timestamp("2025-10-10 19:00:00")
        plan = plan_journey(model, features, stations, station_encoder, origin, destination, event_time, arrive_by_minutes=10)
        print("\nJourney plan:", plan)

    except Exception as e:
        print(f"\n--- FATAL ERROR IN MAIN EXECUTION ---")
        print(f"An unrecoverable error occurred: {e}")
        print("\n**TROUBLESHOOTING CHECKLIST (File Parsing):**")
        print(f"1. **File Existence:** Ensure all files are in the correct location: '{STATION_FILE_PATH}', '{OD2031_PATH}', '{UGZ_PATH}'.")
        print("2. **File Delimiter:** The aggressive parser tries ',', ';', and '\\t'. If parsing fails, open the file and manually confirm the correct delimiter.")
        print("3. **Error Type:** Check the error message (e.g., `FileNotFoundError` means the path is wrong; `ParserError` means the data format is the issue).")