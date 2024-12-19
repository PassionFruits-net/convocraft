from pydantic import BaseModel, Field
from enum import Enum


class Gender(str, Enum):
    male = "male"
    female = "female"

    
class Speaker(BaseModel):
    name: str = Field(..., description="The name of the speaker.")
    role: str = Field(..., description="The role of the speaker in the conversation.")
    gender: Gender = Field(..., description="The gender of the speaker (male or female).")


class Utterance(BaseModel):
    speaker: Speaker
    text: str
    entities: list[str] = Field(..., description="List of entities mentioned in the text.")
    discussion_points: str = Field(..., description="The discussion point related to the text.")


class Conversation(BaseModel):
    utterances: list[Utterance]


class DiscussionPoint(BaseModel):
    text: str = Field(..., description="The main point of the discussion.")
    image_prompt: str = Field(..., description="A prompt to generate an image based on the discussion point.")

class Section(BaseModel):
    focus: str = Field(..., description="The main point of this section.")
    discussion_points: list[DiscussionPoint] = Field(
        ..., 
        description="A list of key points to be discussed in this section."
    )

class ConversationOutline(BaseModel):
    context: str = Field(
        ...,
        description="""A brief introduction to the topic and its importance. 
        Should include character names and a one-liner about their background.
        Make sure that one character name is male and one is female."""
    )
    sections: list[Section] = Field(
        ...,
        description="A list of sections outlining the conversation, each containing a focus and key discussion points."
    )
    speakers: list[Speaker] = Field(
        ...,
        description="""A list of speakers involved in the conversation, each with a name, gender and role."""
    )