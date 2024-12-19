import os
import openai
import streamlit as st

def get_openai_client():
    if "OPENAI_API_KEY" not in st.session_state or not st.session_state["OPENAI_API_KEY"]:
        raise ValueError("OpenAI API Key is not set in session_state.")
    os.environ["OPENAI_API_KEY"] = st.session_state["OPENAI_API_KEY"]
    return openai.OpenAI()
