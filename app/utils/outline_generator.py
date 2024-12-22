import tempfile
import tts_wrapper
import streamlit as st
from pydub import AudioSegment
from itertools import product
from utils.data_models import Gender, ConversationOutline, Section, Speaker
from utils.openai_utils import get_openai_client

def generate_outline_prompt(topic, length):
    image_prompt_details = st.session_state.get("image_prompt_details", "")
    prompt = dict()
    prompt["system"] = "You are a conversation planner."
    prompt["user"] = f"""
    Outline a {length}-minute conversation about the provided topic between two participants.
    Conversation Topic: {topic}
    
    - It is of utmost importance to cover some parts of the topic in as much depth as possible than to cover all of it.
    - The conversation has to have a natural start and ending.
    - Make the outline such that it is possible to break it down and generate LLM prompts for each part of the conversation without losing coherence.
    
    Additionally, generate image prompt details based on the following description: '{image_prompt_details}'.
    
    General instructions for the image_prompts:
    - your prompts must be descriptive of the scene, describe exact element, lighting, mood but not wordy.
    - all prompts must follow a similar theme/style.
    - make sure there is nothing NSFW in the prompts.
    - all scenery must be depicting natural elements, no humans or maps etc.
    - prompts must be specifically tailored for Dall-E
    """
    return prompt

def generate_outline(prompt, model="gpt-4o-2024-08-06"):
    client = get_openai_client()
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": prompt["user"]},
        ],
        response_format=ConversationOutline
        )
    return completion.choices[0].message.parsed

def generate_fake_outline(topic, length):
    outline = ConversationOutline(
        context=f"This is a {length}-minute long conversation about {topic}.", 
        sections=[
            Section(
                focus="Introduction",
                discussion_points=["Introduce the topic", "Discuss the relevance of the topic"]
            ),
            Section(
                focus="Main Discussion",
                discussion_points=["Point 1", "Point 2", "Point 3"]
            ),
            Section(
                focus="Conclusion",
                discussion_points=["Summarize the discussion", "Provide a closing statement"]
            )
        ],
        speakers=[
            Speaker(name="Speaker 1", role="Expert", gender="male"),
            Speaker(name="Speaker 2", role="Moderator", gender="female")
        ]
        )
    return outline

def generate_outline_update_prompt(original_outline, user_instructions):
    prompt = dict()
    prompt["system"] = "You are a conversation planner."
    prompt["user"] = f"""
    You are given the outline of a conversation, and a set of inquiries to make changes. 
    You need to make sure that all changes are reflected in the context as well as all the sections such that the cohesion and consistency of the conversation outline remains intact.
    
    ORIGINAL OUTLINE:
    {original_outline}
    
    INSTRUCTIONS:
    {user_instructions}
    """
    return prompt
