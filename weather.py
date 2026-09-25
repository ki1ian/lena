import os
import requests

from datetime import datetime, timezone, timedelta
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

# Return a more detailed weather forecast for the day given a location
# Base example returns today's high/low and a representative condition
# Returns None if request fails (invalid location, bad API key)
def get_forecast(location):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": location,
        "appid": OWM_API_KEY,
        "units": "imperial"
    }

    response = requests.get(url, params=params)

    # Status code 200 means the request was successful
    # Anything else should be treated as a failure (e.g. 404 for invalid location, 401 for bad API key, etc)
    if response.status_code != 200:
        print(f"Error fetching weather forecast: {response.status_code} - {response.text}")
        return None
    
    # Convert JSON response into Python dictionary
    data = response.json()
    # List of forecasts at 3-hour intervals for the next 5 days
    entries = data["list"]

    # Use designated city's UTC offset (in seconds)
    # Aim here is to avoid dependence on device/server's set location
    utc_offset_seconds = data["city"]["timezone"]
    local_offset = timedelta(seconds=utc_offset_seconds)

    today_local = (datetime.now(timezone.utc) + local_offset).date()

    # Filter to just today's entries
    # Each entry's "dt_txt" field is in the format "YYYY-MM-DD HH:MM:SS"
    # So convert each to the location's local time, then compare
    todays_entries = []
    for entry in entries:
        utc_time = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        local_time = utc_time + local_offset
        
        if local_time.date() == today_local:
            todays_entries.append(entry)

    # If there are no entries for today, return None
    if not todays_entries:
        print("No forecast data available for today.")
        return None
    
    # Extract temperatures from today's entries and calculate high and low
    temps = [entry["main"]["temp"] for entry in todays_entries]
    high = round(max(temps))
    low = round(min(temps))

    # Pick entry closest to midday (12:00) as representative
    midday_entry = min(todays_entries, key=lambda entry: abs(int(entry["dt_txt"][11:13]) - 12))
    description = midday_entry["weather"][0]["description"]

    # Return a dictionary with high, low, and description
    return {"high": high, "low": low, "description": description}