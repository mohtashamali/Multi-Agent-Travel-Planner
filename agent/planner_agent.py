
from agent.llm import get_llm


def planner_agent(state):
    llm = get_llm()

    prompt = f"""
    You are a travel planner. Combine the information below into one
    clear, friendly, day-by-day travel itinerary for the user.

    Trip: {state['start']} to {state['destination']}
    Dates: {state['start_date']} to {state['end_date']}
    People: {state['num_people']}
    Budget: Rs {state['budget']}
    Preferred transport: {state['travel_mode']}
    Interests: {state['interests']}

    ROUTE INFO:
    {state.get('route_info', 'N/A')}

    TRANSPORT INFO:
    {state.get('transport_info', 'N/A')}

    HOTEL INFO:
    {state.get('hotel_info', 'N/A')}

    ACTIVITY INFO:
    {state.get('activity_info', 'N/A')}

    FOOD INFO:
    {state.get('food_info', 'N/A')}

    BUDGET INFO:
    {state.get('budget_info', 'N/A')}

    Format your answer exactly like this:

    Day 1:
    - ...
    Day 2:
    - ...
    (add more days if needed, based on the trip dates)

    Then add these sections:
    Total Estimated Cost:
    Transportation Details:
    Hotel Suggestions:
    Important Places:
    Food Suggestions:
    Travel Tips:
    """

    response = llm.invoke(prompt)

    return {"final_plan": response.content}
