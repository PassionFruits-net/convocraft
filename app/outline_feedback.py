from itertools import product
from utils.data_models import Conversation, Gender, ConversationOutline, Section, Speaker
from utils.openai_utils import get_openai_client

def generate_outline_prompt(topic, length):
    prompt = dict()
    prompt["system"] = "You are a conversation planner."
    prompt["user"] = f"""Outline a {length}-minute conversation about '{topic}' between two participants.
    It is of utmost importance to cover some parts of the topic in as much depth as possible than to cover all of it.
    The conversation has to have a natural start and ending.
    Make the outline such that it is possible to break it down and generate LLM prompts for each part of the conversation without losing coherence.
    DO NOT write anything but the outline itself in markdown format.    
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
    prompt["user"] = f"""You are given the outline of a conversation, and a set of inquiries to make changes. 
    You need to make sure that all changes are reflected in the context as well as all the sections such that the cohesion and consistency of the conversation outline remains intact.
    
    ORIGINAL OUTLINE:
    {original_outline}
    
    INSTRUCTIONS:
    {user_instructions}
    """
    return prompt

def update_outline_button():
        st.header("🔍 Edit Outline")

    st.text_area(
        "Instruct the LLM to make changes to the context and prompts",
        placeholder="""
        - Change the names to Saghar (female) and Egil (male)
        - Change the topic to dark matter
        - Keep the conversation topics as in the original outline 
            but divide the sections such that each section contains ONLY ONE discussion topic 
            (i.e. divide each section in the original outline to as many subsections as there are discussion topics)
        """,
        height=200,
        key="user_change_instructions"
    )

    if st.button("Send Update Instructions to LLM"):
        update_outline_button_callback()

    if "outline" in st.session_state:
        st.write(st.session_state["outline"])

