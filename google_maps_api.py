import json
from serpapi import GoogleSearch
import csv
from datetime import datetime
import os

# Replace with your actual SerpApi API key
SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')

# Define your 10 routes with origins and destinations
routes = [
    {'origin': 'Millennium Makkah Al Naseem Hotel, Third Ring Rd, AL Naseem District, Makkah 21514', 'destination': 'Masjid al-Haram, Al Haram, Makkah 24231'},
    {'origin': 'Ministry of Hajj and Umrah, CQ89+699, Makkah - Jeddah Hwy, Al Hamra Umm Al Jud, Makkah 24321', 'destination': 'Millennium Makkah Al Naseem Hotel, Third Ring Rd, AL Naseem District, Makkah 21514'},
    # Add additional routes here
]

def get_travel_duration(origin, destination):
    params = {
        "engine": "google_maps_directions",
        "start_addr": origin,
        "end_addr": destination,
        "api_key": SERPAPI_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    try:
        # Access the 'directions' list
        directions_list = results.get('directions')
        if not directions_list:
            print(f"No 'directions' found in the response for {origin} to {destination}.")
            return None

        # Ensure 'directions_list' is a list
        if not isinstance(directions_list, list):
            print(f"'directions' is not a list in the response for {origin} to {destination}.")
            return None

        # Use the first direction in the list
        first_direction = directions_list[0]

        # Extract the duration from the first direction
        duration = first_direction.get('duration')
        if not duration:
            print(f"No 'duration' found in the first direction for {origin} to {destination}.")
            return None

        # The duration is a string like "1 hour 15 mins"
        return duration
    except Exception as e:
        print(f"Error getting duration for {origin} to {destination}: {e}")
        return None

def process_routes():
    # Get the current time of the API call
    api_call_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Use a relative path for the CSV file
    csv_file_path = 'travel_durations.csv'


    # Check if the file exists to decide whether to write the header
    file_exists = os.path.isfile(csv_file_path)

    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header only if the file doesn't exist
        if not file_exists:
            writer.writerow(['API Call Time', 'Origin', 'Destination', 'Travel Duration'])
        for route in routes:
            origin = route['origin']
            destination = route['destination']
            duration = get_travel_duration(origin, destination)
            if duration:
                print(f"Travel duration from {origin} to {destination}: {duration}")
                writer.writerow([api_call_time, origin, destination, duration])
            else:
                print(f"Could not get travel duration from {origin} to {destination}")
                writer.writerow([api_call_time, origin, destination, 'N/A'])

if __name__ == "__main__":
    process_routes()





