"""
llm.py

This file sets up the connection to the LLM (the "brain" every agent uses
to think and write text). We use Groq because it is fast and has a free tier.

API used: Groq (https://groq.com/)
Is it free? YES - free tier available.
How to get a key?
    1. Go to https://console.groq.com/keys
    2. Sign up / log in
    3. Click "Create API Key"
    4. Copy it into your .env file as GROQ_API_KEY=xxxxx
"""
import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()  # this reads the .env file so os.getenv can find the key

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]


def get_llm():
    """
    Creates and returns the LLM object every agent will use.
    We use one simple function so all agents share the exact same setup.
    """
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="openai/gpt-oss-120b",  # fast + free model on Groq
        temperature=0.4,  # lower = more focused/less random answers
    )
    return llm


# Quick manual test - only runs if you execute this file directly
if __name__ == "__main__":
    llm = get_llm()
    response = llm.invoke("Say hello in one short sentence.")
    print(response.content)
