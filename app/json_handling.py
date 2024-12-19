import streamlit as st
import json
from pydantic import parse_obj_as
from utils.data_models import Conversation, ConversationOutline
from audio import render_audio_generation_section
from conversation import render_conversation_section

        
def render_conversation_upload_section():
    # Upload conversation JSON
    uploaded_conversation_file = st.file_uploader("Upload Conversation JSON", type="json", key="upload_conversation")
    if uploaded_conversation_file:
        try:
            uploaded_conversation = json.load(uploaded_conversation_file)
            st.session_state["conversation"] = parse_obj_as(Conversation, uploaded_conversation)
            st.success("Conversation uploaded successfully!")
            st.header("📝 Uploaded Conversation")
            st.write(st.session_state["conversation"])
            render_audio_generation_section()
        except Exception as e:
            st.error(f"Failed to upload conversation: {e}")
                    
def render_conversation_download_section():
    # Download conversation as JSON
    if "conversation" in st.session_state:
        conversation_json = st.session_state["conversation"].model_dump_json(indent=2)
        st.download_button(
            label="Download Conversation (JSON)",
            data=conversation_json,
            file_name="conversation.json",
            mime="application/json"
        )
