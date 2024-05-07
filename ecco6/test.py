import csv
import requests

# Load stop data from the CSV file
stops_file = "/Users/razan/OneDrive/Skrivbord/II1302_Ecco6/ecco6/stops.txt"

def get_station_coordinates(station_name):
    with open(stops_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['stop_name'] == station_name:
                return float(row['stop_lat']), float(row['stop_lon'])
    return None, None

# Replace '<YOUR_API_KEY>' with your actual API key
API_KEY = '006e5723cbfb4a6fa1897d9e8fb44d83'

origin_station_name = 'Södertälje centrum station'  # Example origin station name
destination_station_name = 'Stockholm Centralstation'  # Example destination station name

origin_lat, origin_lon = get_station_coordinates(origin_station_name)
destination_lat, destination_lon = get_station_coordinates(destination_station_name)

if origin_lat is None or origin_lon is None:
    print(f"Error: Station '{origin_station_name}' not found in the database.")
    exit()

if destination_lat is None or destination_lon is None:
    print(f"Error: Station '{destination_station_name}' not found in the database.")
    exit()

# Construct the URL for the Trip endpoint with latitude and longitude
url = f"https://journeyplanner.integration.sl.se/v1/TravelplannerV3_1/trip.json?key={API_KEY}&originCoordLat={origin_lat}&originCoordLong={origin_lon}&destCoordLat={destination_lat}&destCoordLong={destination_lon}"

# Send the GET request
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    
    # Extract and process the suggested travel route information
    # Display only the legs where the type is "ST" (station) and the train name contains "PENDELTÅG"
    for trip in data["Trip"]:
        for leg in trip["LegList"]["Leg"]:
            if "Product" in leg and leg["Product"]["catOut"] == "TRAIN" and "PENDELTÅG" in leg["Product"]["name"]:
                pendeltag_line_number = leg["Product"]["name"]
                print("Line Number (PENDELTÅG):", pendeltag_line_number)
                print("Train Information:")
                print("Departure:", leg['Origin']['name'])
                print("Destination:", leg['Destination']['name'])
                print("Departure Time:", leg['Origin']['time'])
                print("Arrival Time:", leg['Destination']['time'])
                print()

else:
    print("Error:", response.status_code)
