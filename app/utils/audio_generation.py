import tts_wrapper
from pydub import AudioSegment

from utils.llm_calls import Conversation


def merge_conversation(conversation_pieces: list) -> Conversation:
    full_conversation = Conversation(utterances=[])
    for conversation in conversation_pieces:
        full_conversation.utterances.extend(conversation.utterances)
    return full_conversation

def list_voices():
    return tts_wrapper.get_voices()


def generate_text_audio(voice, text):
    return tts_wrapper.render(text, voice)


def generate_audio(conversation, voice_mapping, output_file, preview=False):    
    final_audio = AudioSegment.empty()

    for utterance in conversation.utterances:
        speaker = utterance.speaker
        text = utterance.text
        if speaker not in voice_mapping:
            print(f"Voice not defined for speaker {speaker}, skipping.")
            continue
        try:
            print(f"Generating audio for {speaker}: {text[:30]}...")
            audio_segment = generate_text_audio(voice_mapping[speaker], text)
            final_audio += AudioSegment(audio_segment.raw_data, frame_rate=audio_segment.frame_rate, sample_width=audio_segment.sample_width, channels=audio_segment.channels)
        except Exception as e:
            print(f"Failed to generate audio for {speaker}: {e}")
    
    final_audio.export(output_file, format="mp3")
    print(f"Conversation audio saved to {output_file}")