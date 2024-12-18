import streamlit as st
from auth import handle_authentication
from settings import render_sidebar_settings
from outline import render_outline_section

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

# Handle authentication
authenticated = handle_authentication()

if authenticated:
    render_outline_section()

# if authenticated:
#     # Render sections
#     render_outline_section()
#     # render_conversation_section()
#     # render_audio_section()