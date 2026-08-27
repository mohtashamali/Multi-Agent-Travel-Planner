"""
weather_tool.py

This file talks to the Open-Meteo API to get weather information.

API used: Open-Meteo (https://open-meteo.com/)
Is it free? YES - 100% free, no signup, no API key needed at all.
How to get a key? You don't need one!

Open-Meteo has two parts we use:
1. A "geocoding" endpoint - turns a city name like "Goa" into latitude/longitude.
2. A "forecast" endpoint - gives weather for those coordinates.
"""

import requests


def get_coordinates(city_name):
    """
    Turns a city name (like "Goa") into latitude and longitude.
    Returns a tuple: (latitude, longitude) or (None, None) if not found.
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 1}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # If Open-Meteo found the place, it will be inside data["results"]
        if "results" in data and len(data["results"]) > 0:
            place = data["results"][0]
            return place["latitude"], place["longitude"]
        else:
            return None, None

    except Exception as e:
        print("Geocoding API error:", e)
        return None, None


def get_weather(city_name):
    """
    Gets a simple weather forecast for a city.
    Returns a plain text summary that we can hand to the LLM.
    """
    lat, lon = get_coordinates(city_name)

    if lat is None:
        return f"Could not find weather for {city_name} (city not found)."

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Sample response structure from Open-Meteo:
        # {
        #   "daily": {
        #       "time": ["2026-08-25", "2026-08-26", ...],
        #       "temperature_2m_max": [31.2, 30.5, ...],
        #       "temperature_2m_min": [24.1, 23.8, ...],
        #       "precipitation_sum": [2.3, 0.0, ...]
        #   }
        # }

        daily = data["daily"]
        summary_lines = []
        for i in range(min(3, len(daily["time"]))):  # show first 3 days
            day = daily["time"][i]
            max_temp = daily["temperature_2m_max"][i]
            min_temp = daily["temperature_2m_min"][i]
            rain = daily["precipitation_sum"][i]
            summary_lines.append(
                f"{day}: {min_temp}-{max_temp} deg C, rain: {rain}mm"
            )

        return f"Weather forecast for {city_name}:\n" + "\n".join(summary_lines)

    except Exception as e:
        print("Weather API error:", e)
        return f"Could not fetch weather for {city_name} right now."


# Quick manual test - only runs if you execute this file directly
if __name__ == "__main__":
    print(get_weather("Goa"))
