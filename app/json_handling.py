import streamlit as st
import json
from pydantic import parse_obj_as
from utils.llm_calls import Conversation
from utils.audio_generation import list_voices, generate_audio

def render_json_handling():
    # Download conversation as JSON
    if "conversation" in st.session_state:
        conversation_json = st.session_state["conversation"].model_dump_json(indent=2)
        st.download_button(
            label="Download Conversation (JSON)",
            data=conversation_json,
            file_name="conversation.json",
            mime="application/json"
        )

    # Upload conversation JSON
    uploaded_file = st.file_uploader("Upload Conversation JSON", type="json")
    if uploaded_file:
        try:
            uploaded_data = json.load(uploaded_file)
            st.session_state["conversation"] = parse_obj_as(Conversation, uploaded_data)
            st.success("Conversation uploaded successfully!")

            # Display the uploaded conversation
            st.header("📝 Uploaded Conversation")
            st.write(st.session_state["conversation"])

            # Audio generation section becomes available
            render_audio_generation_section()
        except Exception as e:
            st.error(f"Failed to upload conversation: {e}")


def render_audio_generation_section():
    """Renders the audio generation UI for the uploaded or generated conversation."""
    if "conversation" not in st.session_state:
        return

    st.header("🎧 Audio Generation")
    
    # Generate a unique key for the selectbox to avoid conflicts
    voices = list_voices(st.session_state["conversation"])
    selected_voice = st.selectbox(
        "Choose Voice", 
        voices, 
        key="audio_generation_voice_select"  # Unique key
    )
    st.session_state["selected_voice"] = selected_voice

    # Generate Preview Audio
    if st.button("Generate Preview Audio", key="preview_audio_button"):
        with st.spinner("Generating preview audio..."):
            preview_audio_path = generate_audio(
                st.session_state["conversation"],
                selected_voice,
                preview=True
            )
            st.audio(preview_audio_path, format="audio/mp3")
            st.session_state["preview_audio_path"] = preview_audio_path

    # Generate Full Audio
    if st.button("Generate Full Audio", key="full_audio_button"):
        with st.spinner("Generating full audio..."):
            full_audio_path = generate_audio(
                st.session_state["conversation"],
                selected_voice,
                preview=False
            )
            st.audio(full_audio_path, format="audio/mp3")
            st.session_state["full_audio_path"] = full_audio_path

        # Provide a download button for the full audio
        if "full_audio_path" in st.session_state:
            with open(st.session_state["full_audio_path"], "rb") as file:
                st.download_button(
                    label="Download Full Audio",
                    data=file,
                    file_name="conversation.mp3",
                    mime="audio/mp3",
                    key="download_full_audio_button"  # Unique key
                )