import os
import requests
from dotenv import load_dotenv

# Private, free API key from OpenWeatherMap, load from .env file
load_dotenv()
OWM_API_KEY = os.getenv("OWM_API_KEY")

# Return a short weather description given a location
# Returns None if request fails (invalid location, bad API key)
def get_weather(location):
    url = "https://api.openweathermap.org/data/2.5/weather"
    
    # Query parameters for API request:
    # q: location (city name, state code, country code)
    # appid: API key
    # units: "imperial" for Fahrenheit, "metric" for Celsius
    params = {
        "q": location,
        "appid": OWM_API_KEY,
        "units": "imperial"
    }

    response = requests.get(url, params=params)

    # Status code 200 means the request was successful
    # Anything else should be treated as a failure (e.g. 404 for invalid location, 401 for bad API key, etc)
    if response.status_code != 200:
        print(f"Error fetching weather data: {response.status_code} - {response.text}")
        return None
    
    # Convert JSON response into Python dictionary
    data = response.json()
    description = data["weather"][0]["description"]
    temp = data["main"]["temp"]

    return f"{description.capitalize()}, {round(temp)}°F"
