import streamlit as st
from utils.audio_generation import generate_audio, list_voices

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

    if st.button("Generate Preview Audio", key="preview_audio_button"):
        with st.spinner("Generating preview audio..."):
            preview_audio_path = generate_audio(
                st.session_state["conversation"],
                st.session_state["selected_voice"],
                preview=True
            )
            st.audio(preview_audio_path, format="audio/mp3")

    if st.button("Generate Full Audio", key="full_audio_button"):
        with st.spinner("Generating full audio..."):
            full_audio_path = generate_audio(
                st.session_state["conversation"],
                st.session_state["selected_voice"],
                preview=False
            )
            st.audio(full_audio_path, format="audio/mp3")
            with open(full_audio_path, "rb") as file:
                st.download_button(
                    label="Download Full Audio",
                    data=file,
                    file_name="conversation.mp3",
                    mime="audio/mp3"
                )

def render_audio_generation_section():
    if "conversation" not in st.session_state:
        return

    st.header("🎧 Audio Generation")
    voices = list_voices(st.session_state["conversation"])
    st.selectbox(
        "Choose Voice",
        voices,
        key="audio_generation_voice_select"
    )

    if st.button("Generate Preview Audio", key="generate_preview_button"):
        with st.spinner("Generating preview audio..."):
            preview_audio_path = generate_audio(
                st.session_state["conversation"],
                st.session_state["audio_generation_voice_select"],
                preview=True
            )
            st.audio(preview_audio_path, format="audio/mp3")

    if st.button("Generate Full Audio", key="generate_full_audio_button"):
        with st.spinner("Generating full audio..."):
            full_audio_path = generate_audio(
                st.session_state["conversation"],
                st.session_state["audio_generation_voice_select"],
                preview=False
            )
            st.audio(full_audio_path, format="audio/mp3")
            with open(full_audio_path, "rb") as file:
                st.download_button(
                    label="Download Full Audio",
                    data=file,
                    file_name="conversation.mp3",
                    mime="audio/mp3"
                )