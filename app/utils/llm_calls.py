import re
from utils.openai_utils import get_openai_client
from utils.outline_generator import Speaker, Gender
from pydantic import BaseModel

class Utterance(BaseModel):
    speaker: Speaker
    text: str

class Conversation(BaseModel):
    utterances: list[Utterance]

def format_conversation(conversation):
    formatted_conversation = []
    for utterance in conversation.utterances:
        formatted_conversation.append(f"{utterance.speaker}: {utterance.text}")
    return "\n".join(formatted_conversation)

def fetch_conversation_responses(context, prompts, model="gpt-4o-2024-08-06"):
    client = get_openai_client()
    conversartion_pieces = []
    for prompt in prompts:
        messages = [
            {"role": "system", "content": context},
            {"role": "user", "content": prompt},
        ]
        print(f"Calling LLM with context: {context} and prompt: {prompt}")
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
            response_format=Conversation
        )
        conversartion_pieces.append(completion.choices[0].message.parsed)
    return conversartion_pieces

def fetch_fake_conversation_responses(context, prompts):
    utterances = []
    utterances.append(Utterance(speaker=Speaker(name="Speaker1", role="Teacher1", gender=Gender("female")), text=f"Response 1"))
    utterances.append(Utterance(speaker=Speaker(name="Speaker2", role="Teacher2", gender=Gender("male")), text=f"Response 2"))
    conversation_pieces = [Conversation(utterances=utterances) for _ in prompts]
    return conversation_pieces