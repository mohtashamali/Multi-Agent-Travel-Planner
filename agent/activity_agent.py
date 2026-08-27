
from tools.places_tool import find_attractions
from agent.llm import get_llm


def activity_agent(state):
    destination = state["destination"]
    interests = state["interests"]
    start_date = state["start_date"]
    end_date = state["end_date"]

    # Step 1: get real attraction names from the tool
    places = find_attractions(destination, limit=8)

    if places and "error" in places[0]:
        return {"activity_info": f"Could not find attractions: {places[0]['error']}"}

    places_list_text = "\n".join(
        f"- {p.get('name')} ({p.get('address', 'no address')})" for p in places
    )

    # Step 2: ask the LLM to organize these into a day-by-day plan
    llm = get_llm()
    prompt = f"""
    Here is a list of real attractions near {destination}:
    {places_list_text}

    The user is interested in: {interests}
    Trip dates: {start_date} to {end_date}

    Create a simple day-by-day list of places to visit that matches
    their interests. Keep it short and use bullet points per day.
    """
    response = llm.invoke(prompt)

    return {"activity_info": response.content}


# Quick manual test
if __name__ == "__main__":
    test_state = {
        "destination": "Goa",
        "interests": "nature, sightseeing",
        "start_date": "2026-09-10",
        "end_date": "2026-09-13",
    }
    print(activity_agent(test_state))
