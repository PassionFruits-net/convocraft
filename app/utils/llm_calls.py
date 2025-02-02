import openai
import requests
from utils.openai_utils import get_openai_client
from utils.data_models import Speaker, Gender, Conversation, ConversationUtterance, MonologueUtterance, Monologue, TopicOutline, ConversationResponse, MonologueResponse
from utils.conversation_generator import create_segment_prompt, generate_segment_summary
import streamlit as st

def fetch_conversation_responses(context, prompts, outline: TopicOutline, model="gpt-4o") -> list[Conversation | Monologue]:
    """
    Fetch conversation responses from the OpenAI client.

    Args:
        context (str): The context for the conversation.
        prompts (list): List of user prompts.
        outline (TopicOutline): The outline of the conversation.
        model (str): The OpenAI model to use for generating responses.

    Returns:
        list: A list of conversation pieces (responses from the LLM).
    """
    client = get_openai_client()
    conversation_pieces = []
    previous_summary = None
    segment_info = st.session_state.get("conversation_splits", {
        "total_splits": 1,
        "current_split": 0,
        "num_speakers": outline.num_speakers
    })

    outline_dict = outline.model_dump()
    is_monologue = outline.num_speakers == 1
    response_format = MonologueResponse if is_monologue else ConversationResponse
    final_format = Monologue if is_monologue else Conversation

    for i, prompt in enumerate(prompts):
        segment_prompt = create_segment_prompt(
            context, 
            prompt, 
            segment_info,
            previous_summary
        )
        
        try:
            completion = client.beta.chat.completions.parse(
                model=model,
                messages=[
                    {"role": "system", "content": segment_prompt}
                ],
                temperature=0.7,
                max_tokens=4096,
                response_format=response_format
            )
            response = completion.choices[0].message.parsed
            # Konverter til endelig format med outline
            full_response = final_format(outline=outline_dict, utterances=response.utterances)
            conversation_pieces.append(full_response)
            
            previous_summary = generate_segment_summary(full_response)
            
        except Exception as e:
            st.error(f"Error during LLM call for prompt '{prompt}': {e}")
            conversation_pieces.append(final_format(outline=outline_dict, utterances=[]))

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

def get_image_from_url(url):
    """
    Get an image from a URL and return the binary data.

    Args:
        url (str): The URL of the image.

    Returns:
        bytes: The binary data of the image.
    """
    response = requests.get(url)
    return response.content

def generate_images_with_dalle(prompts, stop_signal, api_key):
    """
    Generate images using OpenAI's DALL·E model.

    Args:
        prompts (list): List of text prompts for image generation.
        stop_signal (dict): A dictionary with an "abort" key to monitor stopping.
        api_key (str): API key for authentication.        

    Returns:
        list: A list of generated image data (binary).
    """
    openai.api_key = api_key
    generated_images = []
    client = openai.OpenAI()
    generated_images = []
    image_urls = []

    for i, prompt in enumerate(prompts):
        if stop_signal.get("abort"):
            break
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt, 
                n=1, 
                size="1792x1024"
                )
            image_url = response.data[0].url
            image_urls.append(image_url)
            generated_images.append((prompt, get_image_from_url(image_url)))
        except Exception as e:
            print(f"Error generating image for prompt '{prompt}': {e}")
            generated_images.append((prompt, None))

    return generated_images, image_urls
