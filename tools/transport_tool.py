"""
transport_tool.py

IMPORTANT NOTE ABOUT THIS FILE:
For real train timings/seat availability in India, the official source is
IRCTC, which does NOT offer a free public API. Real flight search APIs
(like Amadeus or Skyscanner) require business approval, OAuth, and are
not simple/free enough for a beginner project.

So instead of pretending to call a live API, this tool builds a simple,
honest ESTIMATE based on distance and average prices. The Transport Agent
will clearly label this as an estimate, not live booking data.

If you want REAL data later, good next steps are:
- Amadeus for Developers (flights) - has a free sandbox tier, but needs OAuth
- IRCTC unofficial APIs (train) - not officially supported, can break anytime

For now, we keep it simple and free.
"""

from tools.route_tool import find_route


def get_transport_estimate(start, destination, travel_mode, num_people):
    """
    Builds a simple estimated transport plan.
    Uses find_route() (from route_tool.py) to get distance/time,
    then estimates a price per person based on average rates in India.
    """
    route_info = find_route(start, destination, travel_mode_to_route_mode(travel_mode))

    if "error" in route_info:
        return {"error": route_info["error"]}

    distance_km = route_info["distance_km"]
    duration_hours = route_info["duration_hours"]

    # Very rough average price-per-km per person in India, by mode.
    # These are only ESTIMATES so the user gets a realistic ballpark figure.
    price_per_km = {
        "car": 6,      # fuel/cab cost roughly split
        "bus": 1.5,
        "train": 1.2,
        "flight": 6.5,
    }

    rate = price_per_km.get(travel_mode, 2)
    price_per_person = round(distance_km * rate)
    total_price = price_per_person * num_people

    return {
        "mode": travel_mode,
        "distance_km": distance_km,
        "duration_hours": duration_hours,
        "estimated_price_per_person": price_per_person,
        "estimated_total_price": total_price,
        "note": "This is an ESTIMATE, not live booking data (see transport_tool.py for why).",
    }


def travel_mode_to_route_mode(travel_mode):
    """
    Converts the user's travel choice into the mode name route_tool.py expects.
    Car and Bus both use real roads, so both map to "drive".
    """
    if travel_mode in ["car", "bus"]:
        return "drive"
    return travel_mode  # "train" or "flight" stay the same


# Quick manual test
if __name__ == "__main__":
    print(get_transport_estimate("Hyderabad", "Kerala", "train", 4))
