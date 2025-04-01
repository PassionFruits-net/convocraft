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

                # Validate required keys
                if all(k in data for k in ("story", "plan_steps", "instruction")):
                    st.session_state.story = data["story"]
                    st.session_state.plan_steps = data["plan_steps"]
                    st.session_state.instruction = data["instruction"]
                    st.success("Story loaded from file!")

                else:
                    st.error("❌ Invalid format. JSON must include 'story', 'plan_steps', and 'instruction'.")

            except json.JSONDecodeError:
                st.error("❌ Failed to parse JSON. Make sure it's a valid .json file.")

    st.title("📚 LongWriter - Story Generator")
    st.markdown("Generate detailed stories from a plan and save them to Google Drive.")

    # Initialize session state
    if "story" not in st.session_state:
        st.session_state.story = ""
    if "voice" not in st.session_state:
        st.session_state.voice = "nova"

    # Text input for the user plan
    plan = st.session_state.get("instruction", "")

    if not uploaded_json:
        plan = st.text_area("✏️ Enter your story plan or outline", height=250)

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

    # Story generation
    if st.button("🚀 Generate Story"):
        if not plan.strip():
            st.warning("Please enter a valid plan.")
        else:
            with st.spinner("Generating story..."):
                story, plan_steps = generate_longwriter_output(plan)
                st.session_state.story = story
                st.session_state.plan_steps = plan_steps
                save_generation_to_jsonl(
                    instruction=plan,
                    plan_steps=plan_steps,
                    story=story
                )            
            st.success("🎉 Story generated!")

    # If a story has been generated, show additional options
    if st.session_state.story:
        story = st.session_state.story
        st.text_area("📝 Generated Story", story, height=400)

        # Offer download
        st.markdown("### 💾 Download or Save Your Story")
        create_download_button(
            data=story,
            filename="longwriter_output.txt",
            mime_type="text/plain",
            label="📥 Download Story"
        )

    if st.session_state.get("plan_steps"):
        st.markdown("### 🧭 Plan Steps")
        for i, step in enumerate(st.session_state["plan_steps"], 1):
            st.markdown(f"**{i}.** {step}")

    # 📥 Download full story/plan as .json
    export_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "instruction": st.session_state.get("instruction", ""),
        "plan_steps": st.session_state.get("plan_steps", []),
        "story": st.session_state.story
    }
    json_str = json.dumps(export_data, ensure_ascii=False, indent=2)

    create_download_button(
        data=json_str,
        filename="longwriter_story.json",
        mime_type="application/json",
        label="📄 Download Story as JSON"
    )

    st.markdown("### 🎨 Generate Image Prompts and Illustrations")

    image_prompt = st.text_input("🖼️ Base style/theme prompt (e.g. Cozy, Cyberpunk, Ancient)")

    if st.button("🎨 Generate Image Prompts + Images"):
        plan_steps = st.session_state.get("plan_steps")
        if not plan_steps:
            st.error("⚠️ Plan steps not found. Please generate or upload a story first.")
        else:
            with st.spinner("Generating DALL·E prompts and images..."):
                from utils.image_prompt_generator import generate_image_prompts_from_steps

                tmp_dir = tempfile.mkdtemp()
                image_dir = os.path.join(tmp_dir, "generated_images")
                os.makedirs(image_dir, exist_ok=True)

                image_prompts = generate_image_prompts_from_steps(image_prompt, plan_steps)
                st.session_state.image_prompts = image_prompts

                # Save prompts
                with open(os.path.join(tmp_dir, "image_prompts.txt"), "w") as f:
                    f.write("\n".join(image_prompts))

                create_download_button(
                    data="\n".join(image_prompts),
                    filename="image_prompts.txt",
                    mime_type="text/plain",
                    label="📝 Download Image Prompts"
                )

                from utils.image_generator import generate_images_from_plan
                image_paths = generate_images_from_plan(image_prompts, image_dir)
                st.session_state.image_paths = image_paths

                # Download ZIP of images
                zip_path = os.path.join(tmp_dir, "generated_images.zip")
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for path in image_paths:
                        zipf.write(path, arcname=os.path.basename(path))

                with open(zip_path, "rb") as f:
                    create_download_button(
                        data=f.read(),
                        filename="generated_images.zip",
                        mime_type="application/zip",
                        label="🖼️ Download All Images (ZIP)"
                    )

        # if st.button("📤 Upload to Google Drive"):
        #     file_link = upload_to_drive(content=story, filename="longwriter_story.txt")
        #     if file_link == "ERROR":
        #         st.error("❌ Upload failed.")
        #     else:
        #         st.success("📂 Uploaded to Drive!")
        #         st.markdown(f"[🔗 View Story File]({file_link})")

    # Voice selection
    st.markdown("### 🎤 Generate Audio")
    voice_options = ["alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"]
    st.session_state.voice = st.selectbox("Choose a voice:", voice_options, index=6)

    if st.button("🔊 Generate Audio"):
        with st.spinner("Generating MP3..."):
            try:
                audio_path = generate_tts_audio(story, voice=st.session_state.voice)
                st.session_state.audio_path = audio_path
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
                    
                with open(audio_path, "rb") as f:
                    audio_bytes = f.read()

                create_download_button(
                    data=audio_bytes,
                    filename="longwriter_audio.mp3",
                    mime_type="audio/mp3",
                    label="🎧 Download Audio"
                )
                    
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
                    # Setup temp dir
                    tmp_dir = tempfile.mkdtemp()
                    image_dir = os.path.dirname(st.session_state.image_paths[0])
                    clip_dir = os.path.join(tmp_dir, "clips")
                    os.makedirs(clip_dir, exist_ok=True)

                    # Generate clips
                    generate_clips_from_images(image_dir=image_dir, output_dir=clip_dir)

                    main_video_path = os.path.join(tmp_dir, "main_video.mp4")
                    combine_clips_and_audio(
                        clips_dir=clip_dir,
                        audio_path=st.session_state.audio_path,
                        output_path=main_video_path
                    )

                    final_video_path = os.path.join(tmp_dir, "final_video.mp4")
                    intro_path = save_uploaded_file(uploaded_intro)
                    outro_path = save_uploaded_file(uploaded_outro)
                    bg_music_path = save_uploaded_file(uploaded_bg_music)

                    finalize_video_with_intro_outro(
                        main_video_path=main_video_path,
                        output_path=final_video_path,
                        intro_path=intro_path,
                        outro_path=outro_path,
                        bg_music_path=bg_music_path
                    )

                    # Upload and download
                    with open(final_video_path, "rb") as f:
                        video_bytes = f.read()

                    drive_link = upload_to_drive(video_bytes, filename="longwriter_final_video.mp4")

                    create_download_button(
                        data=video_bytes,
                        filename="longwriter_final_video.mp4",
                        mime_type="video/mp4",
                        label="📽️ Download Final Video"
                    )
                    st.markdown(f"[🎬 View Video on Drive]({drive_link})")

                except Exception as e:
                    st.error(f"❌ Final video generation failed: {e}")
