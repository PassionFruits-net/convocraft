import json
import os
from utils.data_models import Conversation
import streamlit as st
from pydantic import parse_obj_as
from utils.context_prompts_handler import create_context_and_prompts
from utils.llm_calls import fetch_conversation_responses, fetch_fake_conversation_responses
from utils.conversation_generator import merge_conversation

def render_conversation_upload_section():
    uploaded_conversation_file = st.file_uploader("Upload Conversation JSON", type="json", key="upload_conversation")
    current_conversation = None
    if "current_uploaded_convo_file" in st.session_state:
        current_conversation = st.session_state["current_uploaded_convo_file"]
    if uploaded_conversation_file != current_conversation:
        st.session_state["current_uploaded_convo_file"] = uploaded_conversation_file        
        try:
            uploaded_conversation = json.load(uploaded_conversation_file)
            st.session_state["conversation"] = parse_obj_as(Conversation, uploaded_conversation)
        except Exception as e:
            st.error(f"Failed to upload outline: {e}")

def render_conversation_download_section():
    if "conversation" in st.session_state:
        outline_json = st.session_state["conversation"].model_dump_json(indent=2)
        file_name = st.text_input("Filename for Download", "conversation.json")
        if st.download_button(
            label="Download Conversation",
            data=outline_json,
            file_name=file_name,
            mime="application/json",
            key="download_conversation_button"
        ):
            st.success(f"Conversation saved as {file_name}")
            
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
    with st.sidebar.expander("📝 Conversation Inputs", expanded=False):
        render_conversation_upload_section()

    if "outline" in st.session_state:
        st.header("🗣️ Conversation Generation")
        if st.button("Generate Conversation"):
            with st.spinner("Generating conversation..."):
                generate_conversation_button_callback()

    if "conversation" in st.session_state:
        conversation_as_string = json.dumps(st.session_state["conversation"].model_dump(), indent=2)
        st.text_area("Generated Conversation", value=conversation_as_string, height=300, key="display_conversation", disabled=True)
        render_conversation_download_section()