import tempfile
import tts_wrapper
import streamlit as st
from pydub import AudioSegment
from itertools import product
from utils.data_models import Conversation, Gender, ConversationOutline, Section, Speaker
from utils.openai_utils import get_openai_client

def generate_outline_prompt(topic, length):
    prompt = dict()
    prompt["system"] = "You are a conversation planner."
    prompt["user"] = f"""Outline a {length}-minute conversation about '{topic}' between two participants.
    It is of utmost importance to cover some parts of the topic in as much depth as possible than to cover all of it.
    The conversation has to have a natural start and ending.
    Make the outline such that it is possible to break it down and generate LLM prompts for each part of the conversation without losing coherence.
    DO NOT write anything but the outline itself in markdown format.    
    """
    return prompt


def generate_outline(prompt, model="gpt-4o-2024-08-06"):
    client = get_openai_client()
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": prompt["user"]},
        ],
        response_format=ConversationOutline
        )
    return completion.choices[0].message.parsed


def generate_fake_outline(topic, length):
    outline = ConversationOutline(
        context=f"This is a {length}-minute long conversation about {topic}.", 
        sections=[
            Section(
                focus="Introduction",
                discussion_points=["Introduce the topic", "Discuss the relevance of the topic"]
            ),
            Section(
                focus="Main Discussion",
                discussion_points=["Point 1", "Point 2", "Point 3"]
            ),
            Section(
                focus="Conclusion",
                discussion_points=["Summarize the discussion", "Provide a closing statement"]
            )
        ],
        speakers=[
            Speaker(name="Speaker 1", role="Expert", gender="male"),
            Speaker(name="Speaker 2", role="Moderator", gender="female")
        ]
        )
    return outline

def generate_outline_update_prompt(original_outline, user_instructions):
    prompt = dict()
    prompt["system"] = "You are a conversation planner."
    prompt["user"] = f"""You are given the outline of a conversation, and a set of inquiries to make changes. 
    You need to make sure that all changes are reflected in the context as well as all the sections such that the cohesion and consistency of the conversation outline remains intact.
    
    ORIGINAL OUTLINE:
    {original_outline}
    
    INSTRUCTIONS:
    {user_instructions}
    """
    return prompt

# def update_outline_button_callback():
#     st.header("🔍 Edit Outline")

#     st.text_area(
#         "Instruct the LLM to make changes to the context and prompts",
#         placeholder="""
#         - Change the names to Saghar (female) and Egil (male)
#         - Change the topic to dark matter
#         - Keep the conversation topics as in the original outline 
#             but divide the sections such that each section contains ONLY ONE discussion topic 
#             (i.e. divide each section in the original outline to as many subsections as there are discussion topics)
#         """,
#         height=200,
#         key="user_change_instructions"
#     )

#     if st.button("Send Update Instructions to LLM"):
#         update_outline_button_callback()

#     if "outline" in st.session_state:
#         st.write(st.session_state["outline"])


#### FIXME! Do not belong here! ####
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


def generate_audio_preview_callback():
    conversation = st.session_state["conversation"]
    voice_mapping = st.session_state["selected_voice_mapping"]
    generate_audio(conversation, voice_mapping, preview=True)


def generate_audio_full_callback():
    conversation = st.session_state["conversation"]
    voice_mapping = st.session_state["selected_voice_mapping"]
    generate_audio(conversation, voice_mapping, preview=False)


def generate_audio(conversation, voice_mapping, output_file="conversation.mp3", preview=False):
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

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        final_audio.export(temp_file.name, format="mp3")
        st.audio(temp_file.name, format="audio/mp3")
        return temp_file.name
    else:
        for utterance in conversation.utterances:
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


def render_audio_section():
    if "conversation" not in st.session_state:
        return

    st.header("🎧 Audio Generation")
    voices = list_voices(st.session_state["conversation"])
    st.selectbox(
        "Choose Voice Combination",
        voices,
        key="selected_voice_mapping"
    )

    if st.button("Generate Preview Audio"):
        generate_audio_preview_callback()

    if st.button("Generate Full Audio"):
        generate_audio_full_callback()