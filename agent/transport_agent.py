"""
transport_agent.py

This agent gives transport details: mode, estimated price, duration.
(See tools/transport_tool.py for why prices here are ESTIMATES, not
live booking data - there's no simple free API for real train/flight
prices in India.)
"""

from tools.transport_tool import get_transport_estimate
from agent.llm import get_llm


def transport_agent(state):
    start = state["start"]
    destination = state["destination"]
    travel_mode = state["travel_mode"]
    num_people = state["num_people"]

    # Step 1: get estimated transport numbers from the tool
    transport_data = get_transport_estimate(start, destination, travel_mode, num_people)

    if "error" in transport_data:
        return {"transport_info": f"Could not estimate transport: {transport_data['error']}"}

    # Step 2: ask the LLM to explain it nicely
    llm = get_llm()
    prompt = f"""
    Write a short, friendly summary (3-4 sentences) of this transport plan.
    Clearly mention it is an ESTIMATE, not a live booking price.

    Mode: {travel_mode}
    Distance: {transport_data['distance_km']} km
    Duration: {transport_data['duration_hours']} hours
    Estimated price per person: Rs {transport_data['estimated_price_per_person']}
    Estimated total price for {num_people} people: Rs {transport_data['estimated_total_price']}
    """
    response = llm.invoke(prompt)

    return {
        "transport_info": response.content,
        "transport_cost": transport_data["estimated_total_price"],  # used later by budget agent
    }

