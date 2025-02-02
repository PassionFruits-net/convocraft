import json
import os
from utils.data_models import Conversation, Monologue
import streamlit as st
from pydantic import TypeAdapter
from utils.context_prompts_handler import create_context_and_prompts
from utils.llm_calls import fetch_conversation_responses, fetch_fake_conversation_responses
from utils.conversation_generator import merge_conversation
from utils.token_estimator import TokenEstimator

def generate_conversation_button_callback():
    outline = st.session_state["outline"]
    if os.environ.get("DEBUG_MODE", "").lower() == "true":
        conversation_pieces = fetch_fake_conversation_responses(
            st.session_state["context"], 
            st.session_state["prompts"],
            outline
        )
    else:
        estimator = TokenEstimator()
        num_splits = estimator.estimate_conversation_splits(outline.length_minutes)
        tokens_per_split = estimator.get_tokens_per_split(outline.length_minutes, num_splits)
        
        splits_info = {
            "total_splits": num_splits,
            "tokens_per_split": tokens_per_split,
            "current_split": 0,
            "num_speakers": outline.num_speakers
        }
        st.session_state["conversation_splits"] = splits_info

        all_conversation_pieces = []
        progress_bar = st.progress(0)

        for split_num in range(splits_info["total_splits"]):
            splits_info["current_split"] = split_num
            st.session_state["conversation_splits"] = splits_info
            progress = (split_num + 1) / splits_info["total_splits"]
            progress_bar.progress(progress)

            context, prompts = create_context_and_prompts(outline)
            conversation_pieces = fetch_conversation_responses(context, prompts, outline)
            all_conversation_pieces.extend(conversation_pieces)

            st.info(f"Generated part {split_num + 1} of {splits_info['total_splits']}")

        st.session_state["conversation"] = merge_conversation(all_conversation_pieces, outline)
        progress_bar.empty()

def render_conversation_upload_section():
    uploaded_file = st.file_uploader("Upload Conversation JSON", type="json", key="upload_conversation")
    if uploaded_file is not None:
        try:
            content = json.load(uploaded_file)
            # Bestem type basert på antall speakers i outline
            if content.get("outline", {}).get("num_speakers", 2) == 1:
                model_type = Monologue
            else:
                model_type = Conversation
            st.session_state["conversation"] = TypeAdapter(model_type).validate_python(content)
        except Exception as e:
            st.error(f"Failed to upload conversation: {e}")

def render_conversation_download_section():
    if "conversation" in st.session_state:
        conversation_json = st.session_state["conversation"].model_dump_json(indent=2)
        file_name = st.text_input("Filename for Download", "conversation.json")
        if st.download_button(
            label="Download Conversation",
            data=conversation_json,
            file_name=file_name,
            mime="application/json",
            key="download_conversation_button"
        ):
            st.success(f"Conversation saved as {file_name}")

def render_conversation_section():
    with st.sidebar.expander("💬 Conversation Inputs", expanded=False):
        render_conversation_upload_section()

    if "outline" in st.session_state:
        output_type = "Monologue" if st.session_state["outline"].num_speakers == 1 else "Conversation"
        st.header(f"🗣️ {output_type} Generation")
        if st.button(f"Generate {output_type}"):
            with st.spinner(f"Generating {output_type.lower()}..."):
                generate_conversation_button_callback()

    if "conversation" in st.session_state:
        output_type = "Monologue" if isinstance(st.session_state["conversation"], Monologue) else "Conversation"
        st.header(f"Generated {output_type}")
        conversation_as_string = json.dumps(st.session_state["conversation"].model_dump(), indent=2)
        st.text_area(
            f"Generated {output_type}", 
            value=conversation_as_string, 
            height=300, 
            key="display_conversation", 
            disabled=True
        )
        render_conversation_download_section()