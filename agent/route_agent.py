"""
route_agent.py

This agent figures out the route between the start city and destination.

How it works (simple 2-step pattern used by every agent in this project):
1. Call a TOOL to get real data (here: tools/route_tool.py)
2. Give that raw data to the LLM and ask it to explain it in friendly text

This same pattern repeats in every agent file, so once you understand this
one, you understand them all.
"""

from tools.route_tool import find_route
from agent.llm import get_llm


def travel_mode_to_route_mode(travel_mode):
    """Car and bus both drive on roads, so both map to 'drive'."""
    if travel_mode in ["car", "bus"]:
        return "drive"
    return travel_mode


def route_agent(state):
    """
    state is a dictionary holding all the trip info (see main.py for its shape).
    This function reads what it needs from state, and returns a dictionary
    with ONE new key: "route_info". LangGraph will merge this into the state.
    """
    start = state["start"]
    destination = state["destination"]
    travel_mode = state["travel_mode"]

    # Step 1: call the tool to get real distance/time data
    route_mode = travel_mode_to_route_mode(travel_mode)
    route_data = find_route(start, destination, route_mode)

    if "error" in route_data:
        return {"route_info": f"Could not calculate route: {route_data['error']}"}

    # Step 2: ask the LLM to turn the raw numbers into a friendly sentence
    llm = get_llm()
    prompt = f"""
    Write 2-3 short sentences describing this travel route in a friendly way.

    From: {start}
    To: {destination}
    Mode: {travel_mode}
    Distance: {route_data['distance_km']} km
    Estimated duration: {route_data['duration_hours']} hours

    Keep it short and simple.
    """
    response = llm.invoke(prompt)

    return {"route_info": response.content}


# Quick manual test
if __name__ == "__main__":
    test_state = {"start": "Hyderabad", "destination": "Goa", "travel_mode": "car"}
    print(route_agent(test_state))
