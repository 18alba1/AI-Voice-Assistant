from langchain.pydantic_v1 import BaseModel, Field
import requests
import streamlit as st

class GetWeatherInput(BaseModel):
    city_name: str = Field(description="The name of the city to get the weather forecast for.")

def get_weather(city_name: str) -> str:
    url = "https://yahoo-weather5.p.rapidapi.com/weather"
    querystring = {"location": city_name, "format": "json", "u": "c"}

    headers = {
        "X-RapidAPI-Key": st.secrets["WEATHER_API_KEY"],
        "X-RapidAPI-Host": st.secrets["WEATHER_API_HOST"]
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()
        current_observation = data.get("current_observation", {})
        temperature_celsius = current_observation.get("condition", {}).get("temperature")
        
        if temperature_celsius is not None:
            return f"The current temperature in {city_name} is {temperature_celsius:.2f}°C"
        else:
            return f"Temperature data for {city_name} not available."
    else:
        return "Failed to fetch weather data."
