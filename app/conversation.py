import os
import streamlit as st
from utils.context_prompts_handler import create_context_and_prompts
from utils.llm_calls import fetch_conversation_responses, fetch_fake_conversation_responses
from utils.sync_utils import extract_participant_names, update_context_with_names, update_prompts_with_names
from utils.audio_generation import merge_conversation

def render_conversation_section():
    if "outline" not in st.session_state:
        return

    st.header("🔍 Edit Context & Prompts")
    context, prompts = create_context_and_prompts(st.session_state["outline"])
    st.session_state["context"] = context
    st.session_state["prompts"] = prompts

    # Editable context
    edited_context = st.text_area("Edit Context", context, height=200)
    st.session_state["edited_context"] = edited_context

    # Editable prompts
    st.subheader("Edit Prompts")
    edited_prompts = []
    for i, prompt in enumerate(prompts):
        edited_prompt = st.text_area(f"Edit Prompt {i+1}", prompt, height=100)
        edited_prompts.append(edited_prompt)

    if st.button("Submit Changes"):
        participant_names = extract_participant_names(edited_context)
        st.session_state["context"] = update_context_with_names(edited_context, participant_names)
        st.session_state["prompts"] = update_prompts_with_names(edited_prompts, participant_names)
        st.success("Context and prompts updated successfully!")

    if st.button("Generate Conversation"):
        with st.spinner("Generating conversation..."):
            conversation_pieces = fetch_conversation_responses(st.session_state["context"], st.session_state["prompts"])
            st.session_state["conversation"] = merge_conversation(conversation_pieces)

    if "conversation" in st.session_state:
        st.write(st.session_state["conversation"])
