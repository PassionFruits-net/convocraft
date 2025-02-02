from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class Gender(str, Enum):
    male = "male"
    female = "female"

    
class Speaker(BaseModel):
    name: str = Field(..., description="The name of the speaker.")
    role: str = Field(..., description="The role of the speaker in the conversation/monologue.")
    gender: Gender = Field(..., description="The gender of the speaker (male or female).")

class DiscussionPoint(BaseModel):
    text: str = Field(..., description="The main point of the discussion.")
    image_prompts: Optional[list[str]] = Field(..., description="A list of prompts to generate images based on the discussion point.")


class Section(BaseModel):
    focus: str = Field(..., description="The main point of this section.")
    discussion_points: list[DiscussionPoint] = Field(
        ..., 
        description="A list of key points to be discussed in this section."
    )

class TopicOutline(BaseModel):
    context: str = Field(
        ...,
        description="""A brief introduction to the topic and its importance."""
    )
    sections: list[Section] = Field(
        ...,
        description="A list of sections outlining the conversation/monologue, each containing a focus and key discussion points."
    )
    speakers: list[Speaker] = Field(
        ...,
        description="""A list of speaker(s) involved in the conversation/monologue, each with a name, gender and role. There may be only one speaker."""
    )
    length_minutes: int = Field(
        ...,
        description="The target length of the conversation/monologue in minutes"
    )
    num_speakers: int = Field(
        ...,
        description="Number of speakers in the conversation/monologue (1 for monologue or 2 for conversation)"
    )

class MonologueUtterance(BaseModel):
    speaker: Speaker
    text: str = Field(..., description="The text content of the utterance")
    entities: list[str] = Field(..., description="List of entities mentioned in the text")
    discussion_points: str = Field(..., description="The discussion point related to the text")

class ConversationUtterance(BaseModel):
    speaker: Speaker
    text: str = Field(..., description="The text content of the utterance")
    entities: list[str] = Field(..., description="List of entities mentioned in the text")
    discussion_points: str = Field(..., description="The discussion point related to the text")

class ConversationBase(BaseModel):
    outline: dict = Field(..., description="The outline used to generate this conversation")
    utterances: list[ConversationUtterance | MonologueUtterance] = Field(..., description="List of utterances in the conversation")

class Conversation(ConversationBase):
    utterances: list[ConversationUtterance]

class Monologue(ConversationBase):
    utterances: list[MonologueUtterance]

# For OpenAI response format
class MonologueResponse(BaseModel):
    utterances: list[MonologueUtterance]

class ConversationResponse(BaseModel):
    utterances: list[ConversationUtterance]

class DocumentChunk(BaseModel):
    """
    Represents a single chunk of a document.
    """
    text: str = Field(..., description="Chunk of text from the document.")
    embedding: list[float] = Field(..., description="Vector embedding for this chunk.")

class RetrievedContext(BaseModel):
    """
    Represents a retrieved document context for LLM prompting.
    """
    chunks: list[DocumentChunk] = Field(..., description="List of relevant document chunks.")
    query: str = Field(..., description="The user query used for retrieval.")
