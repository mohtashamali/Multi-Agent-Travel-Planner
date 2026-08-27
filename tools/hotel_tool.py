import os
import requests
from dotenv import load_dotenv
from tools.route_tool import geocode_city

load_dotenv()
GEOAPIFY_API_KEY = st.secrets["GEOAPIFY_API_KEY"]


def find_hotels(city_name, limit=5):
    """
    Returns a list of hotels near the given city.
    Each hotel is a dictionary with name and address.
    """
    lat, lon = geocode_city(city_name)
    if lat is None:
        return [{"error": f"Could not find location for {city_name}"}]

    url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": "accommodation.hotel",
        "filter": f"circle:{lon},{lat},8000",  
        "limit": limit,
        "apiKey": GEOAPIFY_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        hotels = []
        for feature in data.get("features", []):
            props = feature["properties"]
            hotels.append({
                "name": props.get("name", "Unnamed Hotel"),
                "address": props.get("formatted", "Address not available"),
            })

        if not hotels:
            hotels.append({"note": "No hotels found in Geoapify data for this area."})

        return hotels

    except Exception as e:
        print("Hotel API error:", e)
        return [{"error": "Could not fetch hotels right now."}]


# Quick manual test
if __name__ == "__main__":
    print(find_hotels("Goa"))
