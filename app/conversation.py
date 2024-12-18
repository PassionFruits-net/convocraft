import os
import streamlit as st
from utils.context_prompts_handler import create_context_and_prompts
from utils.llm_calls import fetch_conversation_responses, fetch_fake_conversation_responses
from utils.audio_generation import merge_conversation

def generate_conversation_button_callback():
    if os.environ.get("DEBUG_MODE", "").lower() == "true":
        conversation_pieces = fetch_fake_conversation_responses(
            st.session_state["context"], st.session_state["prompts"]
        )
    else:
        st.session_state["context"], st.session_state["prompts"] = create_context_and_prompts(
            st.session_state["outline"]
        )
        conversation_pieces = fetch_conversation_responses(
            st.session_state["context"], st.session_state["prompts"]
        )
    st.session_state["conversation"] = merge_conversation(conversation_pieces)

def render_conversation_section():
    if "outline" not in st.session_state:
        return

    st.header("🔍 Edit Outline")

    st.text_area(
        "Instruct the LLM to make changes to the context and prompts",
        placeholder="""
        - Change the names to Saghar (female) and Egil (male)
        - Change the topic to dark matter
        - Keep the conversation topics as in the original outline 
            but divide the sections such that each section contains ONLY ONE discussion topic 
            (i.e. divide each section in the original outline to as many subsections as there are discussion topics)
        """,
        height=200,
        key="user_change_instructions"
    )

    if st.button("Send Update Instructions to LLM"):
        update_outline_button_callback()

    if "outline" in st.session_state:
        st.write(st.session_state["outline"])

    if st.button("Generate Conversation"):
        with st.spinner("Generating conversation..."):
            generate_conversation_button_callback()

    if "conversation" in st.session_state:
        st.write(st.session_state["conversation"])
