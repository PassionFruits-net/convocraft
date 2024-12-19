import streamlit as st
from utils.audio_generator import generate_audio, list_voices

def on_preview_audio(conversation, selected_voice):
    with st.spinner("Generating preview audio..."):
        preview_audio_path = generate_audio(conversation, selected_voice, preview=True)
        st.session_state["preview_audio_path"] = preview_audio_path

def on_full_audio(conversation, selected_voice):
    with st.spinner("Generating full audio..."):
        full_audio_path = generate_audio(conversation, selected_voice, preview=False)
        st.session_state["full_audio_path"] = full_audio_path

def render_audio_section():
    if "conversation" not in st.session_state:
        return

    st.header("🎧 Audio Generation")
    voices = list_voices(st.session_state["conversation"])
    st.selectbox(
        "Choose Voice Combination",
        voices,
        key="selected_voice"
    )

    st.button(
        "Generate Preview Audio",
        key="preview_audio_button",
        on_click=on_preview_audio,
        args=(st.session_state["conversation"], st.session_state["selected_voice"]),
    )

    if "preview_audio_path" in st.session_state:
        st.audio(st.session_state["preview_audio_path"], format="audio/mp3")

    st.button(
        "Generate Full Audio",
        key="full_audio_button",
        on_click=on_full_audio,
        args=(st.session_state["conversation"], st.session_state["selected_voice"]),
    )

    if "full_audio_path" in st.session_state:
        st.audio(st.session_state["full_audio_path"], format="audio/mp3")
        audio_file_name = st.text_input("Filename for Download", "conversation.mp3")
        with open(st.session_state["full_audio_path"], "rb") as file:
            st.download_button(
                label="Download Full Audio",
                data=file,
                file_name=audio_file_name,
                mime="audio/mp3"
            )
            st.success(f"Full audio saved as {audio_file_name}")            
