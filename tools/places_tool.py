import os
import requests
from dotenv import load_dotenv
from tools.route_tool import geocode_city
import streamlit as st
load_dotenv()
GEOAPIFY_API_KEY = st.secrets["GEOAPIFY_API_KEY"]


def find_places(city_name, category="tourism.sights", limit=8):
    """
    Generic function that finds places of a given category near a city.
    category examples: "tourism.sights", "catering.restaurant"
    """
    lat, lon = geocode_city(city_name)
    if lat is None:
        return [{"error": f"Could not find location for {city_name}"}]

    url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": category,
        "filter": f"circle:{lon},{lat},10000",  # 10km search radius
        "limit": limit,
        "apiKey": GEOAPIFY_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        places = []
        for feature in data.get("features", []):
            props = feature["properties"]
            places.append({
                "name": props.get("name", "Unnamed place"),
                "address": props.get("formatted", "Address not available"),
            })

        if not places:
            places.append({"note": f"No results found for category {category}."})

        return places

    except Exception as e:
        print("Places API error:", e)
        return [{"error": "Could not fetch places right now."}]


def find_attractions(city_name, limit=8):
    """Shortcut function for the Activity Agent."""
    return find_places(city_name, category="tourism.sights", limit=limit)


def find_restaurants(city_name, limit=8):
    """Shortcut function for the Food Agent."""
    return find_places(city_name, category="catering.restaurant", limit=limit)


# Quick manual test
if __name__ == "__main__":
    print(find_attractions("Goa"))
    print(find_restaurants("Goa"))
