import json
from serpapi import GoogleSearch
import csv
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import pandas as pd

# Replace with your actual SerpApi API key
SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')

# Read coordinates from Excel
df = pd.read_excel("Traffic_Locations.xlsx")

# Convert rows to route dictionaries
routes = []
for _, row in df.iterrows():
    routes.append({
        'origin_name': row['From_Location'],
        'destination_name': row['To_Location'],
        'start_coords': row['start_coords'],
        'end_coords': row['end_coords']
    })

def get_travel_duration(start_coords, end_coords):
    params = {
        "engine": "google_maps_directions",
        "start_coords": start_coords,
        "end_coords": end_coords,
        "travel_mode": 0,
        "distance_unit": 0,
        "api_key": SERPAPI_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    try:
        directions_list = results.get('directions')
        if not directions_list or not isinstance(directions_list, list):
            print(f"No valid directions for {start_coords} to {end_coords}.")
            return None, None

        first_direction = directions_list[0]
        duration = first_direction.get('duration', 'N/A')
        distance = first_direction.get('distance', 'N/A')
        return duration, distance
    except Exception as e:
        print(f"Error getting directions: {e}")
        return None, None

def process_routes():
    api_call_time = datetime.now(ZoneInfo("Asia/Riyadh")).strftime("%Y-%m-%d %H:%M:%S")
    csv_file_path = 'travel_durations.csv'
    file_exists = os.path.isfile(csv_file_path)

    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                'API Call Time', 'Origin Name', 'Destination Name',
                'Origin Coords', 'Destination Coords',
                'Travel Duration', 'Distance'
            ])
        for route in routes:
            duration, distance = get_travel_duration(route['start_coords'], route['end_coords'])
            writer.writerow([
                api_call_time,
                route['origin_name'],
                route['destination_name'],
                route['start_coords'],
                route['end_coords'],
                duration if duration else 'N/A',
                distance if distance else 'N/A'
            ])

if __name__ == "__main__":
    process_routes()
