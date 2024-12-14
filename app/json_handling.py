import streamlit as st
import json
from pydantic import parse_obj_as
from utils.llm_calls import Conversation
from utils.outline_generator import ConversationOutline
from audio import render_audio_generation_section
from conversation import render_conversation_section

def render_json_handling():
    # Download outline as JSON
    if "outline" in st.session_state:
        outline_json = st.session_state["outline"].model_dump_json(indent=2)
        st.download_button(
            label="Download Outline (JSON)",
            data=outline_json,
            file_name="outline.json",
            mime="application/json"
        )
    # Download conversation as JSON
    if "conversation" in st.session_state:
        conversation_json = st.session_state["conversation"].model_dump_json(indent=2)
        st.download_button(
            label="Download Conversation (JSON)",
            data=conversation_json,
            file_name="conversation.json",
            mime="application/json"
        )
    
    # Upload outline JSON
    uploaded_outline_file = st.file_uploader("Upload Outline JSON", type="json")
    if uploaded_outline_file:
        try:
            uploaded_outline = json.load(uploaded_outline_file)
            st.session_state["outline"] = parse_obj_as(ConversationOutline, uploaded_outline)
            st.success("Outline uploaded successfully!")

            # Display the uploaded outline
            st.header("📝 Uploaded Outline")
            st.write(st.session_state["outline"])
            
            # Conversation generation section becomes available
            render_conversation_section()
            
        except Exception as e:
            st.error(f"Failed to upload outline: {e}")
    
    # Upload conversation JSON
    uploaded_conversation_file = st.file_uploader("Upload Conversation JSON", type="json")
    if uploaded_conversation_file:
        try:
            uploaded_conversation = json.load(uploaded_conversation_file)
            st.session_state["conversation"] = parse_obj_as(Conversation, uploaded_conversation)
            st.success("Conversation uploaded successfully!")

            # Display the uploaded conversation
            st.header("📝 Uploaded Conversation")
            st.write(st.session_state["conversation"])

            # Audio generation section becomes available
            render_audio_generation_section()
        
        except Exception as e:
            st.error(f"Failed to upload conversation: {e}")
