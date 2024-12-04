import os
import emoji
import streamlit as st
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

# Inject custom CSS
st.markdown(custom_css, unsafe_allow_html=True)

# Title and subtitle with emojis
st.markdown('<h1 class="main-title">ConvoCraft</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">💬 AI-Powered Conversation Generator 🤖</p>',
    unsafe_allow_html=True
)

st.write("")
st.write("")

st.write("🎯 **Features:**")
st.write("📝 Generate conversation outline. ✅")
st.write("🔍 Edit and refine context and prompts. 🔜")
st.write("🎧 Preview and choose audio voices. 🛠️")
st.write("🌐 Seamlessly upload documents for context. 🛠️")
st.write("---")

# Sidebar: Add Logo
st.sidebar.image("/Users/asadisaghar/Downloads/184004124.jpeg", use_container_width=True)

st.sidebar.header("⚙️ Settings")
topic = st.sidebar.text_input("🗣️ Conversation Topic", "Shipwrecks of Europe")
length = st.sidebar.number_input("⏳ Conversation Length (minutes)", min_value=10, max_value=600, value=10)

DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

st.header("📝 Conversation Outline")
if st.button("Generate Outline"):
    if DEBUG_MODE:
        outline = generate_fake_outline(topic, length)
    else:
        outline = generate_outline(topic, length)
    st.session_state["outline"] = outline
if st.session_state.get("outline"):
    st.write(st.session_state["outline"])

if "outline" in st.session_state:
    st.header("🔍 Edit Context & Prompts")
    context, prompts = create_context_and_prompts(st.session_state["outline"])
    
    # Editable Context Section
    if "context" not in st.session_state:
        st.session_state["context"] = context

    edited_context = st.text_area("Edit Context", st.session_state["context"], height=200)
    if st.button("Submit Context Changes"):
        st.session_state["context"] = edited_context
        st.success("Context changes submitted!")        

    # Editable Prompts Section
    if "prompts" not in st.session_state:
        st.session_state["prompts"] = prompts
        
    # edited_prompts = update_prompts(st.session_state["prompts"])
    if st.button("Submit Prompt Changes"):
        st.session_state["prompts"] = edited_prompts
        st.session_state["prompts"] = edited_prompts
        st.success("Prompt changes submitted!")        


    # Generate Conversation
    st.header("🗣️ Generate Conversation")
    if st.button("Generate Conversation"):
        if DEBUG_MODE:
            conversation_pieces = fetch_fake_conversation_responses(
                st.session_state["context"], st.session_state["prompts"]
            )
        else:
            conversation_pieces = fetch_conversation_responses(
                st.session_state["context"], st.session_state["prompts"]
            )
        st.session_state["conversation"] = merge_conversation(conversation_pieces)
        st.write(st.session_state["conversation"])

    # Audio Generation
    if "conversation" in st.session_state:
        st.header("🎧 Audio Generation")
        st.write("Select Voice and Preview")
        voices = list_voices()
        selected_voice = st.selectbox("Choose Voice", voices)
        audio_preview = generate_audio(
            st.session_state["conversation"], 
            selected_voice, 
            output_file="conversation.mp3", 
            preview=True
            )
        st.audio(audio_preview)

        if st.button("Generate Final Audio"):
            final_audio = generate_audio(st.session_state["conversation"], selected_voice)
            st.download_button("Download Audio", data=final_audio, file_name="conversation.mp3")