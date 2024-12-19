import json
import os
from utils.data_models import ConversationOutline
import streamlit as st
from pydantic import parse_obj_as
from utils.outline_generator import (
    generate_outline, 
    generate_fake_outline, 
    generate_outline_prompt, 
    generate_outline_update_prompt
)

def render_outline_upload_section():
    uploaded_outline_file = st.file_uploader("Upload Outline JSON", type="json", key="upload_outline")
    current = None
    if "current_uploaded_file" in st.session_state:
        current = st.session_state["current_uploaded_file"]
    if uploaded_outline_file != current:
        st.session_state["current_uploaded_file"] = uploaded_outline_file        
        try:
            uploaded_outline = json.load(uploaded_outline_file)
            st.session_state["outline"] = parse_obj_as(ConversationOutline, uploaded_outline)
        except Exception as e:
            st.error(f"Failed to upload outline: {e}")


def render_outline_download_section():
    if "outline" in st.session_state:
        outline_json = st.session_state["outline"].model_dump_json(indent=2)
        file_name = st.text_input("Filename for Download", "outline.json")
        if st.download_button(
            label="Download Outline",
            data=outline_json,
            file_name=file_name,
            mime="application/json",
            key="download_outline_button"
        ):
            st.success(f"Outline saved as {file_name}")

def generate_outline_button_callback():
    topic = st.session_state.get("topic", "")
    length = st.session_state.get("length", 10)
    with st.spinner("Generating outline..."):
        if os.environ.get("DEBUG_MODE", "False").lower() == "true":
            outline = generate_fake_outline(topic, length)
        else:
            outline_prompt = generate_outline_prompt(topic, length)
            outline = generate_outline(outline_prompt)
        st.session_state["outline"] = outline

def update_outline_button_callback():
    user_change_instructions = st.session_state.get("user_change_instructions", "")
    if "outline" in st.session_state:
        with st.spinner("Updating outline..."):
            change_prompt = generate_outline_update_prompt(
                st.session_state["outline"], 
                user_change_instructions
            )
            updated_outline = generate_outline(change_prompt)
            st.session_state["outline"] = updated_outline

def render_outline_update_section():
    st.header("🔍 Edit Outline")
    st.text_area(
        "Instruct the LLM to make changes to the context and prompts",
        placeholder="""\n- Change the names to Saghar (female) and Egil (male)\n- Change the topic to dark matter\n- Keep the conversation topics as in the original outline \n    but divide the sections such that each section contains ONLY ONE discussion topic \n    (i.e. divide each section in the original outline to as many subsections as there are discussion topics)\n""",
        height=200,
        key="user_change_instructions"
    )

    st.button("Send Update Instructions to LLM", 
              key="update_outline_button", 
              on_click=update_outline_button_callback)


def render_outline_section():
    with st.sidebar.expander("📝 Outline Inputs", expanded=False):
        render_outline_upload_section()
        st.text_area("🗣️ Conversation Topic", value="", key="topic", height=100)
        st.number_input("⏳ Conversation Length (minutes)", value=10, key="length")
        st.button("Generate Outline", 
                key="generate_outline_button", 
                on_click=generate_outline_button_callback)
    
    if "outline" in st.session_state:
        st.header("📝 Generated Outline")
        outlint_as_string = json.dumps(st.session_state["outline"].model_dump(), indent=2)
        st.text_area("Generated Outline", value=outlint_as_string, height=300, key="display_outline", disabled=True)        
        render_outline_download_section()
        render_outline_update_section()
