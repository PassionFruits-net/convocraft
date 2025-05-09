import streamlit as st
st.set_page_config(page_title="ReviewImages", layout="centered")
import tempfile
import adlfs
import os
import base64
from utils.longwriter_interface import generate_longwriter_output
from utils.read_wrapper import generate_tts_audio
from typing import Union
from utils.image_generator import generate_images_from_plan
from utils.video_builder import (
    generate_clips_from_images,
    combine_clips_and_audio,
    finalize_video_with_intro_outro
)
import json
from auth import handle_authentication
from utils.persistence import PersistedModel
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

fs = adlfs.AzureBlobFileSystem(
    account_name=os.getenv("AZURE_STORAGE_ACCOUNT_NAME"),
    account_key=os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
)


def delete_image(img_index):
    img_path = st.session_state.long_story.image_paths.pop(img_index)
    st.session_state.long_story.image_prompts.pop(img_index)

    stripped = str(img_path).replace("az://", "")
    container, blob_path = stripped.split("/", 1)
    full_path = f"{container}/{blob_path}"

    fs.delete(full_path)


def render_image_grid(image_paths, image_prompts):
    # Ensure state exists
    st.write("### Image Gallery")

    # Show images in rows of 5
    images_per_row = 5
    for i in range(0, len(image_paths), images_per_row):
        cols = st.columns(images_per_row)
        for idx, col in enumerate(cols):
            img_index = i + idx
            if img_index >= len(image_paths):
                break
            img_path = image_paths[img_index]
            img_desc = image_prompts[img_index]
            with col:
                st.image(img_path, use_container_width=True)
                st.caption(img_desc)
                delete_key = f"delete_{img_index}"
                if st.button("Delete", key=delete_key):
                    # Delete image and rerun
                    delete_image(img_index)
                    persist()
                    st.rerun()


if authenticated:
    image_paths = st.session_state.long_story.image_paths
    image_prompts = st.session_state.long_story.image_prompts

    if image_paths:
        paths = []

        for img_path in image_paths:
            stripped = str(img_path).replace("az://", "")
            container, blob_path = stripped.split("/", 1)
            full_path = f"{container}/{blob_path}"

            if not fs.exists(full_path):
                st.warning(f"File not found: {full_path}")
                continue

            with fs.open(full_path, 'rb') as inf:
                image_bytes = inf.read()
                if not image_bytes:
                    st.warning(f"Empty file: {full_path}")
                    continue

                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
                    tmp_img.write(image_bytes)
                    tmp_img.flush()
                    paths.append(tmp_img.name)

        render_image_grid(paths, image_prompts)

    else:
        st.markdown("You don't have any images.")
