import os
import streamlit as st
from utils.audio_generator import generate_audio, list_voices

def on_preview_audio(conversation, selected_voice_1, selected_voice_2):
    with st.spinner("Generating preview audio..."):
        preview_audio_path = generate_audio(conversation, selected_voice_1, selected_voice_2, preview=True)

        if not preview_audio_path:
            st.error("⚠️ Error: `generate_audio` failed to generate preview audio.")
            return

        st.session_state["preview_audio_path"] = preview_audio_path
        st.success(f"✅ Preview audio generated: {preview_audio_path}")

def on_full_audio(conversation, selected_voice_1, selected_voice_2):
    with st.spinner("Generating full audio..."):
        full_audio_path = generate_audio(conversation, selected_voice_1, selected_voice_2, preview=False)

        if not full_audio_path:
            st.error("⚠️ Error: `generate_audio` failed to generate full audio.")
            return

        st.session_state["full_audio_path"] = full_audio_path
        st.success(f"✅ Full audio generated: {full_audio_path}")

def render_audio_section():
    if "conversation" not in st.session_state:
        return

    st.header("🎧 Audio Generation")

    # Get voice options for each speaker
    voice_options_1, voice_options_2 = list_voices(st.session_state["conversation"])

    # Ensure dropdowns exist even if one speaker is missing
    selected_voice_1 = st.selectbox("Choose First Voice", voice_options_1, key="selected_voice_1") if voice_options_1 else None
    selected_voice_2 = st.selectbox("Choose Second Voice", voice_options_2, key="selected_voice_2") if voice_options_2 else None

    if selected_voice_1 and selected_voice_2:
        st.button(
            "Generate Preview Audio",
            key="preview_audio_button",
            on_click=on_preview_audio,
            args=(st.session_state["conversation"], selected_voice_1, selected_voice_2),
        )

        st.button(
            "Generate Full Audio",
            key="full_audio_button",
            on_click=on_full_audio,
            args=(st.session_state["conversation"], selected_voice_1, selected_voice_2),
        )

    if "preview_audio_path" in st.session_state:
        if os.path.exists(st.session_state["preview_audio_path"]) and os.path.getsize(st.session_state["preview_audio_path"]) > 0:
            st.audio(st.session_state["preview_audio_path"], format="audio/mp3")
        else:
            st.error("⚠️ Error: Preview audio file is missing or empty.")

    if "full_audio_path" in st.session_state:
        if os.path.exists(st.session_state["full_audio_path"]) and os.path.getsize(st.session_state["full_audio_path"]) > 0:
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
        else:
            st.error("⚠️ Error: Full audio file is missing or empty.")
