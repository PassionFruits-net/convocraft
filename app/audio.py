import streamlit as st
from utils.audio_generation import generate_audio, list_voices

def render_audio_section():
    if "conversation" not in st.session_state:
        return

    st.header("🎧 Audio Generation")
    voices = list_voices(st.session_state["conversation"])
    selected_voice = st.selectbox("Choose Voice", voices)
    st.session_state["selected_voice"] = selected_voice

    if st.button("Generate Preview Audio"):
        with st.spinner("Generating preview audio..."):
            generate_audio(st.session_state["conversation"], selected_voice, preview=True)

    if st.button("Generate Full Audio"):
        with st.spinner("Generating full audio..."):
            generate_audio(st.session_state["conversation"], selected_voice, preview=False)
