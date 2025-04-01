import json
import os
from utils.data_models import TopicOutline
import streamlit as st
from pydantic import TypeAdapter
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
            st.session_state["outline"] = TypeAdapter(TopicOutline).validate_python(uploaded_outline)
        except Exception as e:
            st.error(f"Failed to upload outline: {e}")


def render_outline_download_section():
    if "outline" in st.session_state:
        outline_json = st.session_state["outline"].model_dump_json(indent=2)
        outline_file_name = st.text_input("Filename for Download", "outline.json")
        if st.download_button(
            label="Download Outline",
            data=outline_json,
            file_name=outline_file_name,
            mime="application/json",
            key="download_outline_button"
        ):
            st.success(f"Outline saved as {outline_file_name}")

def generate_outline_button_callback():
    topic = st.session_state.get("topic", "")
    length = st.session_state.get("length", 10)
    num_speakers = st.session_state.get("num_speakers", 2)
    document_context = st.session_state.get("document_context", None)
    
    with st.spinner("Generating outline..."):
        if os.environ.get("DEBUG_MODE", "False").lower() == "true":
            outline = generate_fake_outline(topic, length, num_speakers)
        else:
            print("DOC CONTEXT", document_context)
            outline_prompt = generate_outline_prompt(
                topic=topic, 
                length=length, 
                num_speakers=num_speakers,
                document_context=document_context
            )
            print("OUTLINE PROMPT", outline_prompt)
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

def render_outline_upload_section():
    uploaded_outline_file = st.file_uploader("Upload Outline JSON", type="json", key="upload_outline")
    current = st.session_state.get("current_uploaded_file", None)

    if uploaded_outline_file != current:
        st.session_state["current_uploaded_file"] = uploaded_outline_file        
        try:
            uploaded_outline = json.load(uploaded_outline_file)
            validated_outline = TypeAdapter(TopicOutline).validate_python(uploaded_outline)

            # ✅ Set the outline
            st.session_state["outline"] = validated_outline

            # ✅ Ensure document_context is set separately
            if hasattr(validated_outline, "document_context"):
                st.session_state["document_context"] = validated_outline.document_context
            else:
                st.session_state["document_context"] = None  # Set to None explicitly if missing

        except Exception as e:
            st.error(f"Failed to upload outline: {e}")

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
        
        if "document_chunks" in st.session_state:
            max_chunks = 3
            selected_chunks = st.session_state["document_chunks"][:max_chunks]
            document_context = "\n".join(selected_chunks)
            
            max_chars = 6000  # roughly 1500 tokens
            if len(document_context) > max_chars:
                document_context = document_context[:max_chars] + "..."
            
            st.session_state["document_context"] = document_context
            
            if len(st.session_state["document_chunks"]) > max_chunks:
                st.info(f"Using first {max_chunks} sections of the document for context. The full document will be used for detailed conversation generation.")
        
        st.text_area(
            "🗣️ Conversation Topic", 
            placeholder="Describe the topic for conversation... (it can be a single word as well as an elaborate scenario)",
            key="topic", 
            height=100
        )
        st.number_input("⏳ Conversation Length (minutes)", value=10, key="length")
        st.number_input(
            "👥 Number of Speakers",
            min_value=1,
            max_value=2,
            value=2,
            key="num_speakers"
        )
        st.number_input(
            "🎨 Number of Image Prompts per Discussion Point", 
            min_value=1, 
            max_value=10, 
            value=5, 
            key="images_per_point"
        )
        st.text_area(
            "🎨 Image Style Details (Optional)", 
            placeholder="Describe the style for image prompt generation (e.g., color, theme, etc.)",
            key="image_prompt_details", 
            height=100
        )
        st.button("Generate Outline", 
                key="generate_outline_button", 
                on_click=generate_outline_button_callback)
    
    if "outline" in st.session_state:
        st.header("📝 Generated Outline")
        outlint_as_string = json.dumps(st.session_state["outline"].model_dump(), indent=2)
        st.text_area("Generated Outline", value=outlint_as_string, height=300, key="display_outline", disabled=True)        
        render_outline_download_section()
        render_outline_update_section()
