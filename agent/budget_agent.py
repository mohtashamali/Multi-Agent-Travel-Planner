
from agent.llm import get_llm


def calculate_nights(start_date, end_date):
    """
    Very simple day-count. Dates are expected as strings like "2026-09-10".
    If parsing fails, we just default to 3 nights.
    """
    from datetime import datetime

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        nights = (end - start).days
        return max(nights, 1)
    except Exception:
        return 3


def budget_agent(state):
    budget = state["budget"]
    num_people = state["num_people"]
    transport_cost = state.get("transport_cost", 0)
    hotel_info = state.get("hotel_info", "No hotel info available.")
    food_info = state.get("food_info", "No food info available.")
    activity_info = state.get("activity_info", "No activity info available.")
    nights = calculate_nights(state["start_date"], state["end_date"])

    llm = get_llm()
    prompt = f"""
    Create a simple estimated cost breakdown for this trip.

    Number of people: {num_people}
    Number of nights: {nights}
    User's total budget: Rs {budget}
    Transport cost (already estimated): Rs {transport_cost}

    Hotel suggestions found earlier:
    {hotel_info}

    Food suggestions found earlier:
    {food_info}

    Activity suggestions found earlier:
    {activity_info}

    Estimate these costs (label everything as an ESTIMATE):
    - Transport cost (use the number given above)
    - Hotel cost (price per night x nights x rooms needed)
    - Food cost (per person per day x days x people)
    - Activity cost
    - Miscellaneous (10% buffer)
    - TOTAL estimated cost

    Also say clearly whether this fits within the user's budget of Rs {budget}.
    Keep the whole answer short and use bullet points.
    """
    response = llm.invoke(prompt)

    return {"budget_info": response.content}


# Quick manual test
if __name__ == "__main__":
    test_state = {
        "budget": 50000,
        "num_people": 4,
        "transport_cost": 8000,
        "hotel_info": "Hotel Sunrise, approx Rs 2500/night",
        "food_info": "Try seafood thali, approx Rs 400/person/meal",
        "activity_info": "Day 1: Beach, Day 2: Fort visit",
        "start_date": "2026-09-10",
        "end_date": "2026-09-13",
    }
    print(budget_agent(test_state))
