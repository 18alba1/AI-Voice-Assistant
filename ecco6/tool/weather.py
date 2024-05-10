from langchain.pydantic_v1 import BaseModel, Field
import requests
import streamlit as st


class WeatherInput(BaseModel):
    city_name: str

def get_weather(input_data: WeatherInput) -> str:
    base_url = "https://ai-weather-by-meteosource.p.rapidapi.com"
    headers = {
        "X-RapidAPI-Key": st.secrets["WEATHER_API_KEY"],
        "X-RapidAPI-Host": "ai-weather-by-meteosource.p.rapidapi.com"
    }

    find_places_url = f"{base_url}/find_places"
    find_places_query = {"text": input_data.city_name, "language": "en"}
    find_places_response = requests.get(find_places_url, headers=headers, params=find_places_query)
    place_id = find_places_response.json()[0]['place_id']

    current_weather_url = f"{base_url}/current"
    current_weather_query = {
        "place_id": place_id,
        "timezone": "auto",
        "language": "en",
        "units": "auto"
    }
    current_weather_response = requests.get(current_weather_url, headers=headers, params=current_weather_query)
    weather_data = current_weather_response.json()

    current_weather = weather_data['current']
    response = f"In {input_data.city_name}, the weather is currently {current_weather['summary']}. "
    response += f"The temperature is {current_weather['temperature']}°C, but it feels like {current_weather['feels_like']}°C. "
    response += f"The wind speed is {current_weather['wind']['speed']} m/s coming from the {current_weather['wind']['dir']} direction, "
    response += f"with gusts up to {current_weather['wind']['gusts']} m/s. "
    response += f"There is {current_weather['precipitation']['type']} precipitation, and the humidity level is {current_weather['humidity']}%. "
    response += f"The UV index is {current_weather['uv_index']}. "
    response += f"The visibility is {current_weather['visibility']} km. "
    response += f"The wind chill is {current_weather['wind_chill']}°C."

    return response

