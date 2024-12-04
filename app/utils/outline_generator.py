from pydantic import BaseModel, Field
from utils.openai_utils import get_openai_client


class Speaker(BaseModel):
    name: str = Field(..., description="The name of the speaker.")
    role: str = Field(..., description="The role of the speaker in the conversation.")

class Section(BaseModel):
    focus: str = Field(..., description="The main point of this section.")
    discussion_points: list[str] = Field(
        ..., 
        description="A list of key points to be discussed in this section."
    )

class ConversationOutline(BaseModel):
    context: str = Field(
        ...,
        description="""A brief introduction to the topic and its importance. 
        Should include character names and a one-liner about their background."""
    )
    sections: list[Section] = Field(
        ...,
        description="A list of sections outlining the conversation, each containing a focus and key discussion points."
    )
    speakers: list[Speaker] = Field(
        ...,
        description="A list of speakers involved in the conversation, each with a name and role."
    )
    
def generate_outline(topic, length, model="gpt-4o-2024-08-06"):
    prompt = f"""Outline a {length}-minute conversation about '{topic}' between two participants.
    It is of utmost importance to cover some parts of the topic in as much depth as possible than to cover all of it.
    The conversation has to have a natural start and ending.
    Make the outline such that it is possible to break it down and generate LLM prompts for each part of the conversation without losing coherence.
    DO NOT write anything but the outline itself in markdown format.    
    """
    client = get_openai_client()
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are a conversation planner."},
            {"role": "user", "content": prompt},
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
            Speaker(name="Speaker 1", role="Expert"),
            Speaker(name="Speaker 2", role="Moderator")
        ]
        )
    return outline