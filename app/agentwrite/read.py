import os
import json
import requests
import wave
import tempfile
from pydub import AudioSegment
from dotenv import load_dotenv

# Load OpenAI API Key
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Ensure API key is set
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API Key! Make sure it's set in .env file.")

# Path to the input file
INPUT_FILE = 'write.jsonl'
OUTPUT_FILE = 'read.mp3'
MAX_TTS_INPUT_LENGTH = 4096  # Adjust as needed based on OpenAI's limits

# ✅ Step 1: Read `write.jsonl` and concatenate all "write" values
def load_text_from_jsonl(file_path):
    text_content = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                if "write" in data and isinstance(data["write"], list):
                    text_content.extend(data["write"])  # Collect all text from "write" key
            except json.JSONDecodeError as e:
                print(f"Skipping a malformed line: {e}")
    
    return "\n\n".join(text_content)

# ✅ Step 2: Break text into smaller chunks that fit within TTS limits
def split_text(text, max_length=MAX_TTS_INPUT_LENGTH):
    """Splits text into chunks that fit within OpenAI TTS limits."""
    chunks = []
    while len(text) > max_length:
        split_index = text[:max_length].rfind(". ")  # Try to split at the last sentence boundary
        if split_index == -1:
            split_index = max_length  # Just cut at max length if no good split point
        chunks.append(text[:split_index + 1].strip())
        text = text[split_index + 1:].strip()
    if text:
        chunks.append(text)
    return chunks

# ✅ Step 3: Get available OpenAI voices
def get_openai_voices():
    voices = ["alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"]
    print("\nAvailable Voices:")
    for i, voice in enumerate(voices):
        print(f"[{i+1}] {voice}")
    
    while True:
        try:
            choice = int(input("Select a voice (1-6): ")) - 1
            if 0 <= choice < len(voices):
                return voices[choice]
            else:
                print("Invalid choice. Please enter a number between 1-6.")
        except ValueError:
            print("Please enter a valid number.")

# ✅ Step 4: Convert text to speech using OpenAI's TTS and save to MP3 files
def generate_tts_chunks(chunks, voice):
    """Generates TTS for each chunk and saves them as MP3 files."""
    temp_files = []
    for i, chunk in enumerate(chunks):
        print(f"\n🔊 Generating Speech for Chunk {i+1}/{len(chunks)}...")

        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "tts-1",
            "voice": voice,
            "input": chunk
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            with open(temp_file.name, "wb") as f:
                f.write(response.content)
            temp_files.append(temp_file.name)
        else:
            print(f"❌ Error in TTS Generation for chunk {i+1}: {response.text}")

    return temp_files

# ✅ Step 5: Merge multiple MP3 files into one
def merge_audio_files(audio_files, output_file):
    """Merges multiple MP3 files into a single MP3 file."""
    print("\n🎼 Merging audio files into one MP3...")

    combined_audio = AudioSegment.empty()
    for file in audio_files:
        segment = AudioSegment.from_mp3(file)
        combined_audio += segment

    combined_audio.export(output_file, format="mp3")
    print(f"✅ Final Audio saved as {output_file}")

    # Clean up temp files
    for file in audio_files:
        os.remove(file)

# ✅ Main Function
if __name__ == "__main__":
    print("📖 Reading 'write.jsonl'...")
    full_text = load_text_from_jsonl(INPUT_FILE)

    if not full_text.strip():
        print("❌ No valid text found in write.jsonl")
        exit(1)

    selected_voice = get_openai_voices()
    text_chunks = split_text(full_text)

    audio_files = generate_tts_chunks(text_chunks, selected_voice)
    
    if audio_files:
        merge_audio_files(audio_files, OUTPUT_FILE)
