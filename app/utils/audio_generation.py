import tempfile
import tts_wrapper
import streamlit as st
from pydub import AudioSegment
from itertools import product
from utils.llm_calls import Conversation
from utils.outline_generator import Gender


def merge_conversation(conversation_pieces: list) -> Conversation:
    full_conversation = Conversation(utterances=[])
    for conversation in conversation_pieces:
        full_conversation.utterances.extend(conversation.utterances)
    return full_conversation


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
    available_voice_combinations = generate_voice_combinations(available_voice_mappings)
    return available_voice_combinations


def generate_text_audio(voice, text):
    return tts_wrapper.render(text, voice)


def generate_audio(conversation, voice_mapping, output_file="conversation.mp3", preview=False):
    """
    Generates audio for the conversation using voice mappings.
    
    Args:
        conversation: The conversation object with utterances.
        voice_mapping: A dictionary mapping speakers to voice models.
        output_file: The file to save the final audio (used if preview=False).
        preview: If True, creates a temporary audio file for preview; 
                 if False, saves the audio to `output_file` and provides a download button.
    """
    final_audio = AudioSegment.empty()

    if preview:
        for utterance in conversation.utterances[:5]:
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

        # Save to a temporary file for preview
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        final_audio.export(temp_file.name, format="mp3")
        st.audio(temp_file.name, format="audio/mp3")
        return temp_file.name
    else:
        for utterance in conversation.utterances[:5]:
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
        
        # Save to the specified output file
        final_audio.export(output_file, format="mp3")
        st.audio(output_file, format="audio/mp3")
        with open(output_file, "rb") as file:
            st.download_button(
                label="Download Conversation Audio",
                data=file,
                file_name="conversation.mp3",
                mime="audio/mp3"
            )
        return output_file