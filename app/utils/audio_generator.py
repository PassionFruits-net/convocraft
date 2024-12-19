import tempfile
import tts_wrapper
import streamlit as st
from pydub import AudioSegment
from itertools import product
from utils.data_models import Gender

def generate_voice_combinations(available_voice_mappings):
    speakers, voices = zip(*available_voice_mappings.items())
    voice_combinations = product(*voices)
    return [dict(zip(speakers, combination)) for combination in voice_combinations]

def list_voices(conversation):
    speakers = [utterance.speaker for utterance in conversation.utterances[:2]]
    available_voice_mappings = {}
    for speaker in speakers:
        if speaker.gender == Gender("female"):
            available_voice_mappings[speaker.name] = ["openai:nova"]
        else:
            available_voice_mappings[speaker.name] = ["openai:alloy", "openai:onyx"]
    return generate_voice_combinations(available_voice_mappings)

def generate_text_audio(voice, text):
    return tts_wrapper.render(text, voice)

def generate_audio(conversation, voice_mapping, output_file="conversation.mp3", preview=False):
    final_audio = AudioSegment.empty()
    utterances = conversation.utterances[:5] if preview else conversation.utterances

    for utterance in utterances:
        speaker = utterance.speaker.name
        text = utterance.text
        if speaker not in voice_mapping:
            st.warning(f"Voice not defined for speaker {speaker}, skipping.")
            continue
        try:
            audio_segment = generate_text_audio(voice_mapping[speaker], text)
            final_audio += AudioSegment(
                audio_segment.raw_data,
                frame_rate=audio_segment.frame_rate,
                sample_width=audio_segment.sample_width,
                channels=audio_segment.channels
            )
        except Exception as e:
            st.error(f"Failed to generate audio for {speaker}: {e}")

    if preview:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        final_audio.export(temp_file.name, format="mp3")
        return temp_file.name
    else:
        final_audio.export(output_file, format="mp3")
        return output_file