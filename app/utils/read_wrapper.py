# utils/read_wrapper.py
import os
import tempfile
import requests
from pydub import AudioSegment
from dotenv import load_dotenv
from typing import List

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TTS_MODEL = "tts-1"
MAX_TTS_INPUT_LENGTH = 4096

def split_text(text: str, max_length=MAX_TTS_INPUT_LENGTH) -> List[str]:
    chunks = []
    while len(text) > max_length:
        split_index = text[:max_length].rfind(". ")
        if split_index == -1:
            split_index = max_length
        chunks.append(text[:split_index + 1].strip())
        text = text[split_index + 1:].strip()
    if text:
        chunks.append(text)
    return chunks

def generate_tts_audio(text: str, voice: str = "nova") -> str:
    if not OPENAI_API_KEY:
        raise ValueError("Missing OpenAI API Key!")

    chunks = split_text(text)
    audio_segments = []

    for i, chunk in enumerate(chunks):
        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": TTS_MODEL,
            "voice": voice,
            "input": chunk
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"TTS chunk failed: {response.text}")

        # Save to temp file
        temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        with open(temp_mp3.name, "wb") as f:
            f.write(response.content)
        audio_segments.append(AudioSegment.from_mp3(temp_mp3.name))
        os.remove(temp_mp3.name)

    # Merge audio
    final_audio = sum(audio_segments[1:], audio_segments[0]) if len(audio_segments) > 1 else audio_segments[0]
    final_path = os.path.join(tempfile.gettempdir(), "longwriter_audio.mp3")
    final_audio.export(final_path, format="mp3")
    return final_path
