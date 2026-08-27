from tools.places_tool import find_restaurants
from agent.llm import get_llm


def food_agent(state):
    destination = state["destination"]
    interests = state["interests"]

    # Step 1: get real restaurant names from the tool
    restaurants = find_restaurants(destination, limit=8)

    if restaurants and "error" in restaurants[0]:
        return {"food_info": f"Could not find restaurants: {restaurants[0]['error']}"}

    restaurant_list_text = "\n".join(
        f"- {r.get('name')} ({r.get('address', 'no address')})" for r in restaurants
    )

    # Step 2: ask the LLM to suggest food + pick restaurants
    llm = get_llm()
    prompt = f"""
    Here is a list of real restaurants near {destination}:
    {restaurant_list_text}

    The user's interests include: {interests}

    Suggest 3-4 must-try local dishes at this destination, and pick a
    few restaurants from the list above worth visiting. Keep it short.
    """
    response = llm.invoke(prompt)

    return {"food_info": response.content}


# Quick manual test
if __name__ == "__main__":
    test_state = {"destination": "Goa", "interests": "food, sightseeing"}
    print(food_agent(test_state))
