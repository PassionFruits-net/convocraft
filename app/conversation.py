import json
import os
from utils.data_models import Conversation
import streamlit as st
from pydantic import TypeAdapter
from utils.context_prompts_handler import create_context_and_prompts
from utils.llm_calls import fetch_conversation_responses, fetch_fake_conversation_responses
from utils.conversation_generator import merge_conversation

def generate_conversation_button_callback():
    if os.environ.get("DEBUG_MODE", "").lower() == "true":
        conversation_pieces = fetch_fake_conversation_responses(
            st.session_state["context"], st.session_state["prompts"]
        )
        st.session_state["conversation"] = merge_conversation(conversation_pieces)
    else:
        splits_info = st.session_state.get("conversation_splits", {
            "total_splits": 1,
            "current_split": 0
        })

        all_conversation_pieces = []
        progress_bar = st.progress(0)

        for split_num in range(splits_info["total_splits"]):
            splits_info["current_split"] = split_num
            st.session_state["conversation_splits"] = splits_info
            progress = (split_num + 1) / splits_info["total_splits"]
            progress_bar.progress(progress)

            context, prompts = create_context_and_prompts(st.session_state["outline"])
            conversation_pieces = fetch_conversation_responses(context, prompts)
            all_conversation_pieces.extend(conversation_pieces)

            st.info(f"Generated part {split_num + 1} of {splits_info['total_splits']}")

        st.session_state["conversation"] = merge_conversation(all_conversation_pieces)
        progress_bar.empty()

def render_conversation_upload_section():
    uploaded_conversation_file = st.file_uploader("Upload Conversation JSON", type="json", key="upload_conversation")
    current_conversation = None
    if "current_uploaded_convo_file" in st.session_state:
        current_conversation = st.session_state["current_uploaded_convo_file"]
    if uploaded_conversation_file != current_conversation:
        st.session_state["current_uploaded_convo_file"] = uploaded_conversation_file        
        try:
            uploaded_conversation = json.load(uploaded_conversation_file)
            st.session_state["conversation"] = TypeAdapter(Conversation).validate_python(uploaded_conversation)
        except Exception as e:
            st.error(f"Failed to upload outline: {e}")

def render_conversation_download_section():
    if "conversation" in st.session_state:
        conversation_json = st.session_state["conversation"].model_dump_json(indent=2)
        conversation_file_name = st.text_input("Filename for Download", "conversation.json")
        if st.download_button(
            label="Download Conversation",
            data=conversation_json,
            file_name=conversation_file_name,
            mime="application/json",
            key="download_conversation_button"
        ):
            st.success(f"Conversation saved as {conversation_file_name}")
            
def render_conversation_section():
    with st.sidebar.expander("💬 Conversation Inputs", expanded=False):
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