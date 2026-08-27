# Multi-Agent Travel Planner

A beginner-friendly AI travel planner where **7 simple agents** work together
(using LangChain + LangGraph + Groq) to build a full trip itinerary.

---

## 1. How the architecture works (in plain language)

Think of it like a **relay race**. Each agent does one small job, then
hands a shared notebook (called `state`) to the next agent:

```
route_agent → transport_agent → hotel_agent → activity_agent
    → food_agent → budget_agent → planner_agent → DONE
```

- **state** is just a Python dictionary. It starts with the user's inputs
  (start city, destination, budget, etc). Every agent reads what it needs
  from `state` and adds its own result back into it.
- By the time it reaches `planner_agent` (the last one), `state` contains
  everything: route info, transport info, hotels, activities, food, and
  budget. `planner_agent` combines it all into the final itinerary.
- **LangGraph** is the tool that manages this relay race. You tell it
  "run route_agent first, then transport_agent, then..." and it handles
  passing `state` along automatically.

Each agent follows the exact same simple 2-step pattern:
1. Call a **tool** (a function that fetches real data from an API)
2. Give that data to the **LLM** (via LangChain) and ask it to explain
   the data in friendly, readable text

Once you understand one agent, you understand all seven - they're all
built the same way on purpose, to keep things simple.

---

## 2. Project structure

```
travel_planner/
│
├── agent/
│   ├── main.py             # Wires all agents together with LangGraph
│   ├── llm.py               # Sets up the Groq LLM connection (shared by all agents)
│   ├── route_agent.py       # Finds the route between start & destination
│   ├── transport_agent.py   # Estimates transport (train/flight/bus/car) cost & time
│   ├── hotel_agent.py       # Finds & suggests hotels
│   ├── activity_agent.py    # Finds attractions, builds day-by-day sightseeing plan
│   ├── food_agent.py        # Suggests local food & restaurants
│   ├── budget_agent.py      # Adds up total estimated cost
│   └── planner_agent.py     # Combines everything into the final itinerary
│
├── tools/
│   ├── __init__.py
│   ├── weather_tool.py      # Open-Meteo API (free, no key) - weather forecast
│   ├── route_tool.py        # Geoapify Geocoding + Routing API - distance/time
│   ├── transport_tool.py    # Estimated transport pricing (no free live API exists)
│   ├── hotel_tool.py        # Geoapify Places API - real hotel names/addresses
│   └── places_tool.py       # Geoapify Places API - attractions & restaurants
│
├── streamlit_app.py         # The web UI (run this to use the app)
├── .env.example              # Copy this to .env and add your real keys
├── requirements.txt
└── README.md                 # You are here
```

We did **not** add a `weather_agent.py` because weather isn't one of the
7 requested agents - `weather_tool.py` is included as a bonus tool you
can plug into any agent later (e.g. add it to `activity_agent.py` to
adjust suggestions based on rain).

---

## 3. The APIs used (and why)

### Groq (the LLM / "brain")
- **What it does:** Runs the AI model that writes all the friendly text.
- **Free?** Yes, free tier available.
- **Get a key:** https://console.groq.com/keys → "Create API Key"
- **Store it:** `.env` → `GROQ_API_KEY=your_key_here`
- **Sample call:** see `agent/llm.py`

### Geoapify (Geocoding, Routing, Places/Hotels/Restaurants)
- **What it does:** Converts city names to coordinates, calculates real
  driving routes, and finds real hotels/attractions/restaurants near a
  location.
- **Free?** Yes, free tier = 3000 requests/day. Requires signup.
- **Get a key:** https://www.geoapify.com/ → Sign up → create a project
  → copy the API key.
- **Store it:** `.env` → `GEOAPIFY_API_KEY=your_key_here`
- **Sample response (Places API):**
  ```json
  { "features": [
      { "properties": { "name": "Hotel Sunrise", "formatted": "MG Road, Goa" } }
  ]}
  ```
  This gets turned into a Python dict and passed to the LLM as plain text
  inside the agent's prompt (see `hotel_agent.py`).

### Open-Meteo (Weather)
- **What it does:** Weather forecast for the destination.
- **Free?** Yes, 100% free, no signup, no key needed at all.
- **Sample call:** see `tools/weather_tool.py`

### Train / Flight live pricing - honest note
There is **no simple free API** for real Indian train or flight prices:
- IRCTC has no official public API.
- Flight APIs (Amadeus, Skyscanner) need business approval / OAuth setup,
  which is too complex for a beginner project.

**Our alternative:** `transport_tool.py` calculates distance (using the
Geoapify/route logic) and multiplies it by an average price-per-km for
each mode, clearly labeled as an **ESTIMATE**. This keeps the project
honest and still useful. If you want real data later, look into the
Amadeus Self-Service free tier.

---

## 4. How LangChain is used
LangChain's `ChatGroq` class (from `langchain-groq`) is what actually
sends our prompts to the Groq LLM and gets a response back. Every agent
calls `get_llm()` from `agent/llm.py` to get the same shared LLM object,
then calls `.invoke(prompt)` to get an answer. That's it - we don't use
any complex LangChain chains, agents-with-tools, or memory objects,
to keep things simple.

## 5. How LangGraph is used
LangGraph's `StateGraph` builds the "flowchart" described in section 1.
- `graph.add_node(name, function)` registers each agent as a step.
- `graph.add_edge(step_a, step_b)` says "after step_a, run step_b".
- `graph.compile()` turns it into a runnable object.
- `.invoke(initial_state)` runs the whole flow start to finish and
  returns the final `state` dictionary.

See `agent/main.py` for the full wiring.

---

## 5. Setup instructions

### Step 1: Install dependencies
```bash
cd travel_planner
pip install -r requirements.txt
```

### Step 2: Add your API keys
```bash
cp .env.example .env
```
Then open `.env` and paste in your real `GROQ_API_KEY` and
`GEOAPIFY_API_KEY` (see section 3 above for how to get them).

### Step 3: Run the app
```bash
streamlit run app.py
```
This opens a browser tab with the trip-planning form.

### Step 4 (optional): Test a single agent from the terminal
Every agent file and tool file has a small test at the bottom
(`if __name__ == "__main__":`). For example:
```bash
python -m agent.route_agent
```
Run it from the **project root folder** (`travel_planner/`), using the
`-m` flag, so Python can find the `agent` and `tools` packages.

### Step 5: Try the example from the spec
In the Streamlit form, enter:
```
Start: Hyderabad
Destination: Kerala
People: 4
Budget: 50000
Travel: Train
```
Click **"Plan My Trip"** and wait ~30-60 seconds for all 7 agents to run.

---

## 6. Common errors & fixes

| Error | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'agent'` | Run commands from the `travel_planner/` root folder, not from inside `agent/` |
| `groq.AuthenticationError` or empty LLM response | Check your `GROQ_API_KEY` in `.env` is correct and has no extra spaces |
| Hotel/route/places functions return `error` | Check your `GEOAPIFY_API_KEY` in `.env`, and check you haven't hit the 3000/day free limit |
| Streamlit page is blank / errors on submit | Look at the terminal running `streamlit run` - it prints the real Python error there |
| `requests.exceptions.ConnectionError` | Check your internet connection; some sandboxed environments block outgoing requests |

---

## 7. Ideas to extend this later
- Add `weather_tool.py`'s data into `activity_agent.py` so rainy days
  suggest indoor activities.
- Run `hotel_agent`, `activity_agent`, and `food_agent` in **parallel**
  in LangGraph instead of one-by-one, to make it faster.
- Add a real flight API (Amadeus free tier) once you're comfortable
  with OAuth.
- Let users pick a hotel from a dropdown instead of the LLM picking one.
