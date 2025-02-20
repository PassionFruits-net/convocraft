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

    if len(speakers) > 2:
        st.warning("More than 2 speakers in the conversation. This is not supported yet.")

    # Ensure we only consider two speakers
    speakers = speakers[:2] if len(speakers) >= 2 else speakers

    # Dictionary to store voice options per speaker
    available_voice_mappings = {}

    for speaker in speakers:
        if speaker.gender == Gender("female"):
            available_voice_mappings[speaker.name] = ["openai:nova", "openai:coral", "openai:sage", "openai:shimmer"]
        else:
            available_voice_mappings[speaker.name] = ["openai:alloy", "openai:onyx", "openai:ash", "openai:echo", "openai:fable"]

    # Extract voices for each speaker separately
    voice_options_1 = available_voice_mappings[speakers[0].name] if len(speakers) > 0 else []
    voice_options_2 = available_voice_mappings[speakers[1].name] if len(speakers) > 1 else []

    return voice_options_1, voice_options_2


def generate_text_audio(voice, text):
    return tts_wrapper.render(text, voice)

import os
import tempfile
from pydub import AudioSegment
import streamlit as st
from utils.audio_generator import generate_text_audio

def generate_audio(conversation, voice1, voice2, output_file="conversation.mp3", preview=False):
    final_audio = AudioSegment.empty()
    utterances = conversation.utterances[:5] if preview else conversation.utterances

    # Create a mapping of speakers to selected voices
    speakers = list(set([utterance.speaker.name for utterance in utterances]))
    if len(speakers) < 2:
        st.warning("Conversation has less than two speakers. Assigning the same voice for all.")
    
    voice_mapping = {speakers[0]: voice1}
    if len(speakers) > 1:
        voice_mapping[speakers[1]] = voice2

    for utterance in utterances:
        speaker = utterance.speaker.name
        text = utterance.text

        if speaker not in voice_mapping:
            st.warning(f"⚠️ Voice not defined for speaker {speaker}, skipping.")
            continue

        try:
            # Generate audio for this utterance
            audio_segment = generate_text_audio(voice_mapping[speaker], text)

            # Ensure the audio is valid before adding
            if audio_segment and len(audio_segment.raw_data) > 0:
                final_audio += AudioSegment(
                    audio_segment.raw_data,
                    frame_rate=audio_segment.frame_rate,
                    sample_width=audio_segment.sample_width,
                    channels=audio_segment.channels
                )
            else:
                st.error(f"❌ Failed to generate valid audio for {speaker}")

        except Exception as e:
            st.error(f"❌ Exception while generating audio for {speaker}: {e}")

    # If no audio was generated, return an error
    if len(final_audio) == 0:
        st.error("🚨 Error: No valid audio was generated. Check voice mappings and text content.")
        return None

    # Export audio (either preview or full)
    if preview:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_file.close()  # Ensure it's closed before writing
        final_audio.export(temp_file.name, format="mp3")
        return temp_file.name
    else:
        final_audio.export(output_file, format="mp3")
        return output_file
