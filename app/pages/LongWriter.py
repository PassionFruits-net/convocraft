import streamlit as st
st.set_page_config(page_title="LongWriter", layout="centered")
import base64
from utils.longwriter_interface import generate_longwriter_output
from utils.drive_utils import upload_to_drive
from utils.read_wrapper import generate_tts_audio
from typing import Union
from utils.image_generator import generate_images_from_plan
from utils.video_builder import (
    generate_clips_from_images,
    combine_clips_and_audio,
    finalize_video_with_intro_outro
)
import tempfile
import os
from utils.longwriter_interface import save_generation_to_jsonl
import json
from datetime import datetime
import zipfile
from utils.image_prompt_generator import generate_image_prompts_from_steps
from auth import handle_authentication
from utils.persistence import PersistedModel
import fsspec
import typing
import pydantic

class LongStory(PersistedModel):
    # FIXME: This could be a hierarchy of PersistedModel with
    # attributes that are themselves PersistedModel subclasses instead
    # of all strins in the top level model...
    instruction: typing.Optional[str] = None
    plan_steps: typing.Optional[list[str]] = None
    story: typing.Optional[str] = None
    image_prompts: typing.Optional[list[str]] = None
    image_paths: typing.Optional[list[pydantic.AnyUrl]] = None
    clip_paths: typing.Optional[list[pydantic.AnyUrl]] = None
    audio_path: typing.Optional[pydantic.AnyUrl] = None
    main_video_path: typing.Optional[pydantic.AnyUrl] = None
    intro_path: typing.Optional[pydantic.AnyUrl] = None
    outro_path: typing.Optional[pydantic.AnyUrl] = None
    bg_music_path: typing.Optional[pydantic.AnyUrl] = None
    final_video_path: typing.Optional[pydantic.AnyUrl] = None

def create_download_button(
    data: Union[str, bytes],
    filename: str,
    mime_type: str,
    label: str = "📥 Download"
):
    """
    Renders a Streamlit download link for a text or binary file.

    Parameters:
    - data: str (text) or bytes (binary content)
    - filename: desired file name for download
    - mime_type: MIME type like 'text/plain' or 'audio/mp3'
    - label: text to display on the download link
    """
    if isinstance(data, str):
        b64 = base64.b64encode(data.encode()).decode()
    elif isinstance(data, bytes):
        b64 = base64.b64encode(data).decode()
    else:
        raise ValueError("Data must be a string or bytes.")

    href = (
        f'<a href="data:{mime_type};base64,{b64}" '
        f'download="{filename}">{label}</a>'
    )
    st.markdown(href, unsafe_allow_html=True)


def persist():
    st.session_state.version = st.session_state.long_story.persist()
    st.query_params["version"] = st.session_state.version

if 'version' not in st.session_state:
    if 'version' in st.query_params:
        st.session_state.version = st.query_params['version']
        print("Loading: ", st.session_state.version)
        st.session_state.long_story = LongStory(__jsonclass__=["persisted_at", st.session_state.version])
        print("Loaded: ", st.session_state.long_story)
    else:
        st.session_state.long_story = LongStory()
        persist()
    
# Custom CSS for styling
st.markdown("""
<style>
    .main-title { font-size: 3rem; font-weight: bold; margin-bottom: 0; }
    .sub-title { font-size: 1.2rem; color: gray; margin-top: 0; }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-title">ConvoCraft</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">💬 AI-Powered Conversation Generator 🤖</p>', unsafe_allow_html=True)

# Add logo
logo_path = "app/passionfruits.jpeg"
st.sidebar.image(logo_path, use_container_width=True)

# Handle authentication
authenticated = handle_authentication()

if authenticated:

    with st.sidebar:
        st.markdown("### 📂 Load a Story (Optional)")
        uploaded_json = st.file_uploader("Upload saved story (.json)", type=["json"])

        if uploaded_json:
            try:
                data = json.load(uploaded_json)
                st.session_state.long_story = LongStory(**data)
                persist()
                st.success("Story loaded from file!")
            except json.JSONDecodeError:
                st.error("❌ Failed to parse JSON. Make sure it's a valid .json file.")

    st.title("📚 LongWriter - Story Generator")
    st.markdown("Generate detailed stories from a plan and save them to Google Drive.")

    # Initialize session state
    if "voice" not in st.session_state:
        st.session_state.voice = "nova"

    # Text input for the user plan
    plan = st.session_state.long_story.instruction or ""
    plan = st.text_area("✏️ Enter your story plan or outline", height=250, value=plan)

    # Story generation
    if st.button("🚀 Generate Story"):
        if not plan.strip():
            st.warning("Please enter a valid plan.")
        else:
            with st.spinner("Generating story..."):
                st.session_state.long_story.instruction = plan
                persist()
                story, plan_steps = generate_longwriter_output(plan)
                st.session_state.long_story.story = story
                st.session_state.long_story.plan_steps = plan_steps
                persist()
            st.success("🎉 Story generated!")

    # If a story has been generated, show additional options
    if st.session_state.long_story.story:
        st.text_area("📝 Generated Story", st.session_state.long_story.story, height=400)

    if st.session_state.long_story.plan_steps:
        st.markdown("### 🧭 Plan Steps")
        for i, step in enumerate(st.session_state.long_story.plan_steps, 1):
            st.markdown(f"**{i}.** {step}")

    st.markdown("### 🎨 Generate Image Prompts and Illustrations")

    image_prompt = st.text_input("🖼️ Base style/theme prompt (e.g. Cozy, Cyberpunk, Ancient)")

    if st.button("🎨 Generate Image Prompts + Images"):
        plan_steps = st.session_state.long_story.plan_steps
        if not plan_steps:
            st.error("⚠️ Plan steps not found. Please generate or upload a story first.")
        else:
            with st.spinner("Generating DALL·E prompts and images..."):
                from utils.image_prompt_generator import generate_image_prompts_from_steps

                image_prompts = generate_image_prompts_from_steps(image_prompt, plan_steps)
                st.session_state.long_story.image_prompts = image_prompts
                persist()

                image_paths = generate_images_from_plan(image_prompts)
                st.session_state.long_story.image_paths = image_paths
                persist()

    # Voice selection
    st.markdown("### 🎤 Generate Audio")
    voice_options = ["alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"]
    st.session_state.voice = st.selectbox("Choose a voice:", voice_options, index=6)

    if st.button("🔊 Generate Audio"):
        with st.spinner("Generating MP3..."):
            try:
                st.session_state.long_story.audio_path = generate_tts_audio(story, voice=st.session_state.voice)
                persist()
                st.success("Audio generated!")

                # drive_link = upload_to_drive(
                #     content=open(audio_path, "rb").read(),
                #     filename="longwriter_audio.mp3"
                # )
                # if drive_link == "ERROR":
                #     st.error("❌ Audio upload failed.")
                # else:
                #     st.success("📤 Audio Uploaded to Drive!")
                #     st.markdown(f"[🎧 Listen to Audio]({drive_link})")
                    
                # with fsspec.open(st.session_state.long_story.audio_path, "rb") as f:
                #    audio_bytes = f.read()

                # create_download_button(
                #     data=audio_bytes,
                #     filename="longwriter_audio.mp3",
                #     mime_type="audio/mp3",
                #     label="🎧 Download Audio"
                # )
                    
            except Exception as e:
                st.error(f"❌ Error generating audio: {e}")


    if st.session_state.get("audio_path") and st.session_state.get("image_paths"):
        st.markdown("### 🎬 Combine Audio + Images into Video")

        # Optional uploads
        uploaded_intro = st.file_uploader("Upload Intro Clip", type=["mp4", "mov", "qt"])
        uploaded_outro = st.file_uploader("Upload Outro Clip", type=["mp4", "mov", "qt"])
        uploaded_bg_music = st.file_uploader("Upload Background Music", type=["mp3"])

        if st.button("🎬 Generate Final Video"):
            with st.spinner("Generating final video..."):
                try:
                    st.session_state.long_story.intro_path = persistence.persist_file(uploaded_intro, uploaded_intro.name)
                    st.session_state.long_story.outro_path = persistence.persist_file(uploaded_outro, uploaded_intro.name)
                    st.session_state.long_story.bg_music_path = persistence.persist_file(uploaded_bg_music, uploaded_intro.name)
                    persist()

                    st.session_state.long_story.clip_paths = generate_clips_from_images(st.session_state.image_paths)
                    persist()
                
                    st.session_state.long_story.main_video_path = combine_clips_and_audio(
                        clip_paths = st.session_state.long_story.clip_paths,
                        audio_path = st.session_state.long_story.audio_path)
                    persist()

                    st.session_state.long_story.final_video_path = finalize_video_with_intro_outro(
                        main_video_path=st.session_state.long_story.main_video_path,
                        intro_path=st.session_state.long_story.intro_path,
                        outro_path=st.session_state.long_story.outro_path,
                        bg_music_path=st.session_state.long_story.bg_music_path)
                    persist()

                    # # Upload and download
                    # with open(final_video_path, "rb") as f:
                    #     video_bytes = f.read()

                    # drive_link = upload_to_drive(video_bytes, filename="longwriter_final_video.mp4")

                    # create_download_button(
                    #     data=video_bytes,
                    #     filename="longwriter_final_video.mp4",
                    #     mime_type="video/mp4",
                    #     label="📽️ Download Final Video"
                    # )
                    # st.markdown(f"[🎬 View Video on Drive]({drive_link})")

                except Exception as e:
                    st.error(f"❌ Final video generation failed: {e}")
