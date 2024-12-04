import re
from utils.openai_utils import get_openai_client
from pydantic import BaseModel

class Utterance(BaseModel):
    speaker: str
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
    utterances = [Utterance(speaker=f"Speaker {n}", text=f"Response {n}") for n in range(10)]
    conversation_pieces = [Conversation(utterances=utterances) for _ in prompts]
    return conversation_pieces