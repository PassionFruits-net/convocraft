import streamlit as st

def render_sidebar_settings():
    st.sidebar.header("⚙️ Settings")
    topic = st.sidebar.text_area("🗣️ Conversation Topic", "Shipwrecks of Europe", height=100)
    length = st.sidebar.number_input("⏳ Conversation Length (minutes)", min_value=10, max_value=600, value=10)
    return topic, length
