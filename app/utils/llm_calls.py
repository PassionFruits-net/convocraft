import openai
import requests
from utils.openai_utils import get_openai_client
from utils.data_models import Speaker, Gender, Conversation, Utterance

def fetch_conversation_responses(context, prompts, model="gpt-4o-2024-08-06") -> list[Conversation]:
    """
    Fetch conversation responses from the OpenAI client.

    Args:
        context (str): The context for the conversation.
        prompts (list): List of user prompts.
        model (str): The OpenAI model to use for generating responses.

    Returns:
        list: A list of conversation pieces (responses from the LLM).
    """
    client = get_openai_client()
    conversation_pieces = []  

    for prompt in prompts:
        messages = [
            {"role": "system", "content": context},
            {"role": "user", "content": prompt},
        ]
        try:
            completion = client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=4096,
                response_format=Conversation
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
