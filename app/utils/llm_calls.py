from utils.openai_utils import get_openai_client
from utils.outline_generator import Speaker, Gender
from pydantic import BaseModel, Field

class Utterance(BaseModel):
    speaker: Speaker
    text: str
    entities: list[str] = Field(..., description="List of entities mentioned in the text.")
    discussion_points: str = Field(..., description="The discussion point related to the text.")

class Conversation(BaseModel):
    utterances: list[Utterance]

def format_conversation(conversation):
    formatted_conversation = []
    for utterance in conversation.utterances:
        formatted_conversation.append(f"{utterance.speaker}: [{utterance.text}, {utterance.entities}, {utterance.discussion_points}]")
    return "\n".join(formatted_conversation)

def fetch_conversation_responses(context, prompts, model="gpt-4o-2024-08-06"):
    """
    Fetch conversation responses from the OpenAI client.

    Args:
        context (str): The context for the conversation.
        prompts (list): List of user prompts.
        model (str): The OpenAI model to use for generating responses.

    Returns:
        list: A list of conversation pieces (responses from the LLM).
    """
    client = get_openai_client()  # Ensure this is defined elsewhere in your project
    conversation_pieces = []  # Corrected typo in variable name

    for prompt in prompts:
        messages = [
            {"role": "system", "content": context},
            {"role": "user", "content": prompt},
        ]

        print(f"Calling LLM with context:\n{context}\n\nand prompt:\n{prompt}\n")

        try:
            completion = client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=4096,
                response_format=Conversation  # Ensure Conversation schema is defined
            )
            response = completion.choices[0].message.parsed
            conversation_pieces.append(response)
        except Exception as e:
            print(f"Error during LLM call for prompt '{prompt}': {e}")
            conversation_pieces.append({"error": str(e), "prompt": prompt})

    return conversation_pieces

def fetch_fake_conversation_responses(context, prompts):
    conversation_pieces = []
    for i, prompt in enumerate(prompts):
        utterances = [
            Utterance(
                speaker=Speaker(name="Speaker1", role="Role1", gender=Gender("female")),
                text=f"Fake response to prompt {i+1}: '{prompt}' based on context: '{context}'"
            ),
            Utterance(
                speaker=Speaker(name="Speaker2", role="Role2", gender=Gender("male")),
                text=f"Additional fake response to prompt {i+1}: '{prompt}'"
            )
        ]
        conversation_pieces.append(Conversation(utterances=utterances))
    return conversation_pieces
