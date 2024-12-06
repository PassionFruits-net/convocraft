import os
import emoji
import streamlit as st
from utils.openai_utils import get_openai_client
from utils.outline_generator import generate_outline, generate_fake_outline
from utils.context_prompts_handler import create_context_and_prompts
from utils.llm_calls import fetch_conversation_responses, fetch_fake_conversation_responses, format_conversation
from utils.audio_generation import merge_conversation, generate_audio, list_voices

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
st.sidebar.header("⚙️ Settings")

# Input field for OPENAI_API_KEY
if "OPENAI_API_KEY" not in st.session_state:
    st.session_state["OPENAI_API_KEY"] = ""

st.sidebar.text_input(
    "🔑 OpenAI API Key",
    value=st.session_state["OPENAI_API_KEY"],
    type="password",
    key="OPENAI_API_KEY"
)

try:
    openai_client = get_openai_client()
except ValueError as e:
    st.error(str(e))
    
topic = st.sidebar.text_input("🗣️ Conversation Topic", "Shipwrecks of Europe")
length = st.sidebar.number_input("⏳ Conversation Length (minutes)", min_value=10, max_value=600, value=10)

DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

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

if "outline" in st.session_state:
    st.header("🔍 Edit Context & Prompts")
    context, prompts = create_context_and_prompts(st.session_state["outline"])
    
    if "context" not in st.session_state:
        st.session_state["context"] = context

    edited_context = st.text_area("Edit Context", st.session_state["context"], height=200)
    if st.button("Submit Context Changes"):
        st.session_state["context"] = edited_context

    if "prompts" not in st.session_state:
        st.session_state["prompts"] = prompts

    st.subheader("Edit Prompts")
    with st.expander("Edit Prompts (Click to Expand)"):
        edited_prompts = []
        for i, prompt in enumerate(st.session_state["prompts"]):
            edited_prompts.append(st.text_area(f"Edit Prompt {i+1}", prompt, height=100))

        if st.button("Submit Prompt Changes"):
            st.session_state["prompts"] = edited_prompts

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
