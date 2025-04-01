import streamlit as st
from auth import handle_authentication
from outline import render_outline_section
from conversation import render_conversation_section
from audio import render_audio_section
from text_to_image import render_image_generation_section
from document_section import render_document_section

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
    render_document_section()
    render_outline_section()
    render_conversation_section()
    render_audio_section()
    render_image_generation_section()
