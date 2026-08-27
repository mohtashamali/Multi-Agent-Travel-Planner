"""
route_tool.py

This file calculates the route (distance + time) between two cities.

API used: Geoapify (https://www.geoapify.com/)
Is it free? YES - free tier gives 3000 requests/day, but you DO need to sign up
            for a free API key.
How to get a key?
    1. Go to https://www.geoapify.com/
    2. Click "Get Started" / "Sign Up" (free account)
    3. Create a project, copy the API key
    4. Put it in your .env file as GEOAPIFY_API_KEY=xxxxx

We use two Geoapify endpoints:
    1. Geocoding API -> turns a city name into latitude/longitude
    2. Routing API    -> turns two coordinates into distance + travel time
"""

import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()  
# GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")
GEOAPIFY_API_KEY = st.secrets["GEOAPIFY_API_KEY"]


def geocode_city(city_name):
    """
    Turns a city name into (latitude, longitude) using Geoapify.
    Returns (None, None) if the city cannot be found.
    """
    url = "https://api.geoapify.com/v1/geocode/search"
    params = {"text": city_name, "apiKey": GEOAPIFY_API_KEY, "limit": 1}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Sample response shape:
        # { "features": [ { "geometry": {"coordinates": [lon, lat]}, ... } ] }
        features = data.get("features", [])
        if not features:
            return None, None

        lon, lat = features[0]["geometry"]["coordinates"]
        return lat, lon

    except Exception as e:
        print("Geocoding API error:", e)
        return None, None


def find_route(start, destination, travel_mode="drive"):
    """
    Finds the distance and estimated travel time between two cities.

    travel_mode can be: "drive" (car/bus), "bicycle", or "walk".
    Geoapify's free routing does not support trains/flights directly,
    so for "train" or "flight" we estimate using straight-line distance
    and an average speed instead (see the note below).
    """
    start_lat, start_lon = geocode_city(start)
    dest_lat, dest_lon = geocode_city(destination)

    if start_lat is None or dest_lat is None:
        return {"error": f"Could not find coordinates for {start} or {destination}"}

    
    if travel_mode in ["train", "flight"]:
        distance_km = straight_line_distance_km(start_lat, start_lon, dest_lat, dest_lon)

        if travel_mode == "flight":
            avg_speed_kmh = 700 
        else:
            avg_speed_kmh = 60  

        duration_hours = round(distance_km / avg_speed_kmh, 1)

        return {
            "distance_km": round(distance_km, 1),
            "duration_hours": duration_hours,
            "mode": travel_mode,
            "note": "Estimated using straight-line distance (no live routing API for this mode).",
        }

   
    url = "https://api.geoapify.com/v1/routing"
    params = {
        "waypoints": f"{start_lat},{start_lon}|{dest_lat},{dest_lon}",
        "mode": travel_mode,  # "drive" for car/bus
        "apiKey": GEOAPIFY_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

       
        props = data["features"][0]["properties"]
        distance_km = round(props["distance"] / 1000, 1)  # meters -> km
        duration_hours = round(props["time"] / 3600, 1)  # seconds -> hours

        return {
            "distance_km": distance_km,
            "duration_hours": duration_hours,
            "mode": travel_mode,
            "note": "Real road route from Geoapify Routing API.",
        }

    except Exception as e:
        print("Routing API error:", e)
        return {"error": "Could not calculate route right now."}


def straight_line_distance_km(lat1, lon1, lat2, lon2):
    """
    A simple formula (Haversine formula) to calculate straight-line distance
    between two points on Earth. Used as a fallback for train/flight estimates.
    """
    from math import radians, sin, cos, sqrt, atan2

    R = 6371  # Earth's radius in km

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    d_lat = lat2 - lat1
    d_lon = lon2 - lon1

    a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


# Quick manual test
if __name__ == "__main__":
    print(find_route("Hyderabad", "Goa", "drive"))
