import streamlit as st
from utils.outline_generator import generate_outline, generate_fake_outline

def render_outline_section(topic, length):
    st.header("📝 Conversation Outline")
    if st.button("Generate Outline"):
        with st.spinner("Generating outline..."):
            outline = generate_fake_outline(topic, length) if st.session_state.get("DEBUG_MODE") else generate_outline(topic, length)
            st.session_state["outline"] = outline

    if "outline" in st.session_state:
        st.write(st.session_state["outline"])
