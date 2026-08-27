from tools.hotel_tool import find_hotels
from agent.llm import get_llm


def hotel_agent(state):
    destination = state["destination"]
    budget = state["budget"]
    num_people = state["num_people"]

    # Step 1: get real hotel names/addresses from the tool
    hotels = find_hotels(destination, limit=5)

    if hotels and "error" in hotels[0]:
        return {"hotel_info": f"Could not find hotels: {hotels[0]['error']}"}

    # change the  list of hotel dict into plain text 
    hotel_list_text = "\n".join(
        f"- {h.get('name')} ({h.get('address', 'no address')})" for h in hotels
    )

    # ask the LLM to suggest and estimate prices
    llm = get_llm()
    prompt = f"""
    Here is a list of real hotels near {destination}:
    {hotel_list_text}

    The user's total trip budget is Rs {budget} for {num_people} people.

    Suggest 2-3 of these hotels that would suit a mid-range budget trip.
    For each, give an approximate price per night (label it as an ESTIMATE).
    Keep the answer short - a few bullet points.
    """
    response = llm.invoke(prompt)

    return {"hotel_info": response.content}

