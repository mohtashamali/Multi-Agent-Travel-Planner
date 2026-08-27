"""
main.py

This file connects all 7 agents together using LangGraph.

WHAT IS LANGGRAPH DOING HERE?
LangGraph lets us build a simple "flowchart" of agents. Each agent is a
"node". We connect nodes with "edges" to say which agent runs next.
All agents share one dictionary called "state" - each agent reads what
it needs from state, and adds its own result back into state.

Our flow is simple and sequential (one after another):

    route_agent -> transport_agent -> hotel_agent -> activity_agent
    -> food_agent -> budget_agent -> planner_agent -> END

(Agents don't run in parallel here to keep things easy to understand.
 A more advanced version could run route/hotel/activity/food at the same
 time, but sequential is simpler for a beginner project.)
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END

from agent.route_agent import route_agent
from agent.transport_agent import transport_agent
from agent.hotel_agent import hotel_agent
from agent.activity_agent import activity_agent
from agent.food_agent import food_agent
from agent.budget_agent import budget_agent
from agent.planner_agent import planner_agent


class TripState(TypedDict, total=False):
    """
    This describes every possible key that can exist in our shared state
    dictionary. "total=False" means not all keys are required at once -
    they get added step by step as each agent runs.
    """
    # ---- inputs (filled in by the user) ----
    start: str
    destination: str
    start_date: str
    end_date: str
    num_people: int
    budget: int
    travel_mode: str
    interests: str

    # ---- outputs (filled in by each agent) ----
    route_info: str
    transport_info: str
    transport_cost: int
    hotel_info: str
    activity_info: str
    food_info: str
    budget_info: str
    final_plan: str


def build_graph():
    """
    Builds and returns the LangGraph workflow (the "flowchart" of agents).
    """
    graph = StateGraph(TripState)

    # Register each agent function as a node in the graph
    graph.add_node("route_agent", route_agent)
    graph.add_node("transport_agent", transport_agent)
    graph.add_node("hotel_agent", hotel_agent)
    graph.add_node("activity_agent", activity_agent)
    graph.add_node("food_agent", food_agent)
    graph.add_node("budget_agent", budget_agent)
    graph.add_node("planner_agent", planner_agent)

    # Tell the graph where to start
    graph.set_entry_point("route_agent")

    # Connect the nodes in order (this is the "flowchart" part)
    graph.add_edge("route_agent", "transport_agent")
    graph.add_edge("transport_agent", "hotel_agent")
    graph.add_edge("hotel_agent", "activity_agent")
    graph.add_edge("activity_agent", "food_agent")
    graph.add_edge("food_agent", "budget_agent")
    graph.add_edge("budget_agent", "planner_agent")
    graph.add_edge("planner_agent", END)  # END means "stop here, we're done"

    return graph.compile()  # compile() turns our graph into something runnable


def plan_trip(start, destination, start_date, end_date, num_people, budget, travel_mode, interests):
    """
    This is the main function the Streamlit app (or anyone) calls.
    It builds the graph, runs it with the user's trip details, and
    returns the final state (which includes state["final_plan"]).
    """
    workflow = build_graph()

    initial_state = {
        "start": start,
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "num_people": num_people,
        "budget": budget,
        "travel_mode": travel_mode,
        "interests": interests,
    }

    # .invoke() runs every node in order and returns the final combined state
    final_state = workflow.invoke(initial_state)
    return final_state

