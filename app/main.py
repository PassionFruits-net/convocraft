import json
import os
import yaml
from dotenv import load_dotenv
from pydantic import parse_obj_as
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import LoginError
from utils.outline_generator import generate_outline, generate_fake_outline
from utils.context_prompts_handler import create_context_and_prompts
from utils.llm_calls import Conversation, fetch_conversation_responses, fetch_fake_conversation_responses
from utils.audio_generation import merge_conversation, generate_audio, list_voices
from utils.sync_utils import extract_participant_names, update_context_with_names, update_prompts_with_names

# Custom CSS for styling
custom_css = """
<style>
    .main-title {
        font-size: 3rem; /* Larger font size for the main title */
        font-weight: bold;
        margin-bottom: 0; /* Remove bottom margin for tighter spacing */
    }
    .sub-title {
        font-size: 1.2rem; /* Smaller font size for the subtitle */
        color: gray; /* Optional: Make the subtitle less prominent */
        margin-top: 0; /* Remove top margin for tighter spacing */
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Load configuration from config.yaml
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Create the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    auto_hash=True
)

# Title and subtitle
st.markdown('<h1 class="main-title">ConvoCraft</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">💬 AI-Powered Conversation Generator 🤖</p>', unsafe_allow_html=True)
st.write("")
st.write("")

st.write("🎯 **Features:**")
st.write("📝 Generate conversation outline. ✅")
st.write("🔍 Edit and refine context and prompts. 🔜")
st.write("🎧 Preview and choose audio voices. ✅")
st.write("🌐 Seamlessly upload documents for context. 🛠️")
st.write("---")

# Sidebar
st.sidebar.image("app/184004124.jpeg", use_container_width=True)

# Login widget
try:
    authenticator.login("sidebar")
except LoginError as e:
    st.error(e)

if st.session_state["authentication_status"]:
    authenticator.logout(location="sidebar")
    st.write(f'Welcome *{st.session_state["name"]}*')
    load_dotenv()
    st.session_state["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')

# Sidebar settings
st.sidebar.header("⚙️ Settings")
topic = st.sidebar.text_area(
    "🗣️ Conversation Topic", 
    "Shipwrecks of Europe", 
    height=100  # Adjust the height to make it visually larger
)
length = st.sidebar.number_input(
    "⏳ Conversation Length (minutes)", 
    min_value=2, 
    max_value=600, 
    value=2
)
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

uploaded_file = st.file_uploader("Upload Conversation JSON", type="json")

if uploaded_file:
    try:
        # Load the JSON data from the uploaded file
        uploaded_data = json.load(uploaded_file)

        # Parse the JSON data back into a Conversation object
        st.session_state["conversation"] = parse_obj_as(Conversation, uploaded_data)
        st.success("Conversation uploaded successfully!")
    except Exception as e:
        st.error(f"Failed to upload conversation: {e}")
        
# Generate outline
st.header("📝 Conversation Outline")
if st.button("Generate Outline"):
    with st.spinner("Generating outline..."):
        if DEBUG_MODE:
            outline = generate_fake_outline(topic, length)
        else:
            outline = generate_outline(topic, length)
        st.session_state["outline"] = outline

if "outline" in st.session_state:
    st.write(st.session_state["outline"])

# Edit context and prompts
if "outline" in st.session_state:
    st.header("🔍 Edit Context & Prompts")

    # Initialize context and prompts
    if "context" not in st.session_state:
        context, prompts = create_context_and_prompts(st.session_state["outline"])
        st.session_state["context"] = context
        st.session_state["prompts"] = prompts

    # Editable context
    edited_context = st.text_area("Edit Context", st.session_state["context"], height=200)
    st.session_state["edited_context"] = edited_context

    # Editable prompts
    st.subheader("Edit Prompts")
    with st.expander("Edit Prompts (Click to Expand)"):
        edited_prompts = []
        for i, prompt in enumerate(st.session_state["prompts"]):
            edited_prompt = st.text_area(f"Edit Prompt {i+1}", prompt, height=100)
            edited_prompts.append(edited_prompt)
        st.session_state["edited_prompts"] = edited_prompts

    # Synchronization logic
    if st.button("Submit Changes"):
        # Extract participant names from context
        participant_names = extract_participant_names(st.session_state["edited_context"])

        # Update context and prompts based on participant names
        updated_context = update_context_with_names(st.session_state["edited_context"], participant_names)
        updated_prompts = update_prompts_with_names(st.session_state["edited_prompts"], participant_names)

        # Save updates to session state
        st.session_state["context"] = updated_context
        st.session_state["prompts"] = updated_prompts

        st.success("Context and prompts updated successfully!")

    # Generate conversation
    st.header("🗣️ Generate Conversation")
    if st.button("Generate Conversation"):
        with st.spinner("Generating conversation..."):
            if DEBUG_MODE:
                conversation_pieces = fetch_fake_conversation_responses(
                    st.session_state["context"], st.session_state["prompts"]
                )
            else:
                conversation_pieces = fetch_conversation_responses(
                    st.session_state["context"], st.session_state["prompts"]
                )
            st.session_state["conversation"] = merge_conversation(conversation_pieces)

    if "conversation" in st.session_state:
        st.write(st.session_state["conversation"])

# Display conversation and add download button
if "conversation" in st.session_state:
    # Serialize the Conversation object to JSON
    conversation_json = st.session_state["conversation"].model_dump_json(indent=2)

    # Create a download button for the JSON file
    st.download_button(
        label="Download Conversation (JSON)",
        data=conversation_json,
        file_name="conversation.json",
        mime="application/json"
    )

    
# Audio generation
if "conversation" in st.session_state:
    st.header("🎧 Audio Generation")

    if "selected_voices" not in st.session_state:
        st.session_state["selected_voices"] = None

    voices = list_voices(st.session_state["conversation"])
    selected_voices = st.selectbox("Choose Voice", voices, index=0)
    st.session_state["selected_voices"] = selected_voices

    if "preview_audio_path" not in st.session_state:
        st.session_state["preview_audio_path"] = None
    if "full_audio_path" not in st.session_state:
        st.session_state["full_audio_path"] = None

    if st.session_state["selected_voices"]:
        if st.button("Generate Preview Audio"):
            with st.spinner("Generating preview audio..."):
                preview_audio_path = generate_audio(
                    st.session_state["conversation"],
                    st.session_state["selected_voices"],
                    preview=True
                )
                st.session_state["preview_audio_path"] = preview_audio_path

        if st.button("Generate Full Audio"):
            with st.spinner("Generating full audio..."):
                full_audio_path = generate_audio(
                    st.session_state["conversation"],
                    st.session_state["selected_voices"],
                    preview=False
                )
                st.session_state["full_audio_path"] = full_audio_path

        if st.session_state["preview_audio_path"]:
            st.subheader("Preview Audio")
            st.audio(st.session_state["preview_audio_path"], format="audio/mp3")

        if st.session_state["full_audio_path"]:
            st.subheader("Full Audio")
            st.audio(st.session_state["full_audio_path"], format="audio/mp3")
            with open(st.session_state["full_audio_path"], "rb") as file:
                st.download_button(
                    label="Download Full Audio",
                    data=file,
                    file_name="conversation.mp3",
                    mime="audio/mp3"
                )
