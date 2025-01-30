import streamlit as st
from utils.data_models import ConversationOutline, Section, Speaker
from utils.openai_utils import get_openai_client
from utils.token_estimator import TokenEstimator

def generate_outline_prompt(topic, length):
    image_prompt_details = st.session_state.get("image_prompt_details", "")
    images_per_point = st.session_state.get("images_per_point", 5)

    estimator = TokenEstimator()
    num_splits = estimator.estimate_conversation_splits(length)
    tokens_per_split = estimator.get_tokens_per_split(length, num_splits)

    st.session_state["conversation_splits"] = {
        "total_splits": num_splits,
        "tokens_per_split": tokens_per_split,
        "current_split": 0
    }

    prompt = dict()
    prompt["system"] = "You are a conversation planner."
    prompt["user"] = f"""
    This is part 1 of {num_splits} for a {length}-minute conversation.
    Target token count for this part: {tokens_per_split}

    Topic: {topic}

    Instructions:
    - Create an outline that can be naturally continued in subsequent parts
    - Each part should be self-contained but connect smoothly to others
    - Include approximately {tokens_per_split} tokens worth of conversation
    - Generate exactly {images_per_point} image prompts for each discussion point

    Additional image prompt details: '{image_prompt_details}'

    General instructions for image_prompts:
    - Descriptive scene, elements, lighting, mood but concise
    - Consistent theme/style
    - No NSFW content
    - Natural elements only, no humans or maps
    - Dall-E optimized
    """
    return prompt

def generate_outline(prompt, model="gpt-4o-2024-08-06"):
    client = get_openai_client()
    length = st.session_state.get("length", 10)
    
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": prompt["user"]},
        ],
        response_format=ConversationOutline
    )
    outline = completion.choices[0].message.parsed
    outline.length_minutes = length
    return outline

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