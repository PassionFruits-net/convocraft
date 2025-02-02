import streamlit as st
from utils.data_models import TopicOutline, Section, Speaker
from utils.openai_utils import get_openai_client
from utils.token_estimator import TokenEstimator

def generate_outline_prompt(topic, length, num_speakers, document_context=None):
    image_prompt_details = st.session_state.get("image_prompt_details", "")
    images_per_point = st.session_state.get("images_per_point", 5)
    
    estimator = TokenEstimator()
    num_splits = estimator.estimate_conversation_splits(length)
    tokens_per_split = estimator.get_tokens_per_split(length, num_splits)

    st.session_state["conversation_splits"] = {
        "total_splits": num_splits,
        "tokens_per_split": tokens_per_split,
        "current_split": 0,
        "num_speakers": num_speakers
    }

    prompt = dict()
    prompt["system"] = """You are a content creator. Your task is to create a detailed outline 
    for a conversation or monologue that accurately reflects the content and context of the provided document.
    Focus on the main themes and key points from the document context."""
    
    base_prompt = f"""
    Create a {length}-minute conversation/monologue outline.
    Number of speakers: {num_speakers}
    Topic: {topic}
    """

    if document_context:
        base_prompt += f"""
        DOCUMENT CONTEXT:
        {document_context}

        Instructions:
        - Extract and focus on the main themes and key concepts from the document
        - Organize the discussion points around these core themes
        - Include 2-3 specific references or quotes from the document
        - Ensure discussion points build on each other logically
        """
    
    prompt["user"] = base_prompt + f"""
    Additional Requirements:
    - Create {num_splits} main sections
    - Include 2-3 focused discussion points per section
    - Generate {images_per_point} image prompts per discussion point
    - If num_speakers is 1, make it a monologue

    Image prompt style: '{image_prompt_details}'
    - Keep image prompts concise but descriptive
    - Focus on mood, lighting, and key visual elements
    - Avoid human figures and maps
    - Must be suitable for Dall-E
    """

    return prompt

def generate_outline(prompt, model="gpt-4o"):
    client = get_openai_client()
    length = st.session_state.get("length", 10)
    num_speakers = st.session_state.get("num_speakers", 2)
    
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": prompt["user"]},
        ],
        response_format=TopicOutline
    )
    outline = completion.choices[0].message.parsed
    outline.length_minutes = length
    return outline

def generate_fake_outline(topic, length):
    outline = TopicOutline(
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