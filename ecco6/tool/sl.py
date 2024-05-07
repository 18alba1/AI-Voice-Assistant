import difflib
import csv
import requests
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import StructuredTool
import streamlit as st

stops_file = "/Users/alex/Documents/GitHub/Ecco6py/II1302_Ecco6/ecco6/tool/stops.txt"

def get_station_coordinates(station_name):
    with open(stops_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        station_names = [row['stop_name'].lower() for row in reader]

    closest_matches = difflib.get_close_matches(station_name.lower(), station_names, n=1, cutoff=0.6)
    if closest_matches:
        closest_station_name = closest_matches[0]
        with open(stops_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['stop_name'].lower() == closest_station_name:
                    return float(row['stop_lat']), float(row['stop_lon'])
    return None, None


API_KEY = st.secrets["SL_RESEPLANERARE_API_KEY"]

class GetTravelSuggestionsInput(BaseModel):
    origin_station_name: str = Field(description="The name of the origin station.")
    destination_station_name: str = Field(description="The name of the destination station.")

def get_travel_suggestions(origin_station_name: str, destination_station_name: str) -> str:
    origin_lat, origin_lon = get_station_coordinates(origin_station_name)
    destination_lat, destination_lon = get_station_coordinates(destination_station_name)

    if origin_lat is None or origin_lon is None:
        return f"Error: Station '{origin_station_name}' not found in the database."

    if destination_lat is None or destination_lon is None:
        return f"Error: Station '{destination_station_name}' not found in the database."

    url = f"https://journeyplanner.integration.sl.se/v1/TravelplannerV3_1/trip.json?key={API_KEY}&originCoordLat={origin_lat}&originCoordLong={origin_lon}&destCoordLat={destination_lat}&destCoordLong={destination_lon}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        found_lines = 0
        travel_suggestions = ""

        for trip in data["Trip"]:
            for leg in trip["LegList"]["Leg"]:
                if "Product" in leg and leg["Product"]["catOut"] == "TRAIN" and "PENDELTÅG" in leg["Product"]["name"]:
                    pendeltag_line_number = leg["Product"]["name"]
                    travel_suggestions += f"Line Number (PENDELTÅG): {pendeltag_line_number}\n"
                    travel_suggestions += "Train Information:\n"
                    travel_suggestions += f"Departure: {leg['Origin']['name']}\n"
                    travel_suggestions += f"Destination: {leg['Destination']['name']}\n"
                    travel_suggestions += f"Departure Time: {leg['Origin']['time']}\n"
                    travel_suggestions += f"Arrival Time: {leg['Destination']['time']}\n\n"
                    found_lines += 1
                    if found_lines == 2:
                        break
            if found_lines == 2:
                break
        return travel_suggestions
    else:
        return f"Error: {response.status_code}"
