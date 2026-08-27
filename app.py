"""
streamlit_app.py

This is the web page the user sees. It collects trip details in a form,
then calls plan_trip() from agent/main.py to run all 7 agents and show
the final itinerary.

HOW TO RUN THIS FILE:
    streamlit run streamlit_app.py
"""

import streamlit as st
from agent.main import plan_trip

st.set_page_config(page_title="Multi-Agent Travel Planner", page_icon="🧳")

st.title("🧳 Multi-Agent Travel Planner")
st.write("Fill in your trip details below and let the AI agents plan your trip!")

# --- Input form ---
with st.form("trip_form"):
    start = st.text_input("Starting location", "Hyderabad")
    destination = st.text_input("Destination", "Goa")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Travel date")
    with col2:
        end_date = st.date_input("Return date")

    num_people = st.number_input("Number of people", min_value=1, value=2)
    budget = st.number_input("Budget (Rs)", min_value=1000, value=30000, step=1000)

    travel_mode = st.selectbox("Travel preference", ["car", "train", "flight", "bus"])
    interests = st.text_input("Interests (comma separated)", "food, sightseeing, nature")

    submitted = st.form_submit_button("Plan My Trip")

# --- When the user clicks "Plan My Trip" ---
if submitted:
    with st.spinner("Our AI agents are planning your trip... this may take a minute."):
        try:
            result = plan_trip(
                start=start,
                destination=destination,
                start_date=str(start_date),
                end_date=str(end_date),
                num_people=int(num_people),
                budget=int(budget),
                travel_mode=travel_mode,
                interests=interests,
            )
            st.success("Your trip plan is ready!")
            st.markdown(result["final_plan"])

            # Optional: let the user see what each agent found individually
            with st.expander("See details from each agent"):
                st.subheader("Route")
                st.write(result.get("route_info"))
                st.subheader("Transport")
                st.write(result.get("transport_info"))
                st.subheader("Hotels")
                st.write(result.get("hotel_info"))
                st.subheader("Activities")
                st.write(result.get("activity_info"))
                st.subheader("Food")
                st.write(result.get("food_info"))
                st.subheader("Budget")
                st.write(result.get("budget_info"))

        except Exception as e:
            st.error(f"Something went wrong: {e}")
