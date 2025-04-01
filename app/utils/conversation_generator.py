from utils.data_models import Conversation, Monologue, TopicOutline
from utils.llm_calls import get_openai_client
import streamlit as st


from collections import Counter

def deduplicate_utterances(utterances, n=3):
    """
    Removes duplicate utterances by checking for repeated n-grams (default: trigrams).
    """
    seen = set()
    filtered_utterances = []

    for utterance in utterances:
        # Extract the text content (modify this if `text` is stored under another attribute)
        text = getattr(utterance, "text", None)  # Fallback if `text` isn't an attribute

        if not text:  # Skip empty or improperly formatted utterances
            filtered_utterances.append(utterance)
            continue

        words = text.split()
        n_grams = {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}

        if any(ng in seen for ng in n_grams):
            continue  # Skip repeated content

        seen.update(n_grams)
        filtered_utterances.append(utterance)

    return filtered_utterances


def merge_conversation(conversation_pieces: list, outline: TopicOutline) -> Conversation | Monologue:
    """
    Merges conversation segments while avoiding redundant utterances.
    """
    outline_dict = outline.model_dump()

    if outline.num_speakers == 1:
        full_monologue = Monologue(outline=outline_dict, utterances=[])
        for piece in conversation_pieces:
            full_monologue.utterances.extend(piece.utterances)

        # Apply deduplication
        full_monologue.utterances = deduplicate_utterances(full_monologue.utterances)
        return full_monologue

    else:
        full_conversation = Conversation(outline=outline_dict, utterances=[])
        for piece in conversation_pieces:
            full_conversation.utterances.extend(piece.utterances)

        # Apply deduplication
        full_conversation.utterances = deduplicate_utterances(full_conversation.utterances)
        return full_conversation

def merge_conversation_old(conversation_pieces: list, outline: TopicOutline) -> Conversation | Monologue:
    outline_dict = outline.model_dump()
    if outline.num_speakers == 1:
        full_monologue = Monologue(outline=outline_dict, utterances=[])
        for piece in conversation_pieces:
            full_monologue.utterances.extend(piece.utterances)
        return full_monologue
    else:
        full_conversation = Conversation(outline=outline_dict, utterances=[])
        for piece in conversation_pieces:
            full_conversation.utterances.extend(piece.utterances)
        return full_conversation

def create_segment_prompt(context, prompt, segment_info, previous_summary=None):
    """
    Generate a prompt for a specific segment of the conversation.
    """
    segment_num = segment_info["current_split"] + 1
    total_segments = segment_info["total_splits"]
    num_speakers = segment_info.get("num_speakers", 2)
    previous_entities = segment_info.get("previous_entities", [])
    document_context = st.session_state.get("document_context", None)

    base_prompt = f"""
    🔹 SEGMENT {segment_num} OF {total_segments}

    📌 CONTEXT:
    {context}

    📖 SECTION CONTENT:
    {prompt}
    """

    if document_context:
        base_prompt += f"\n📄 DOCUMENT CONTEXT:\n{document_context}"

    base_prompt += f"""
    🔍 PREVIOUSLY MENTIONED ENTITIES:
    {', '.join(previous_entities) if previous_entities else 'None'}

    ✅ INSTRUCTIONS:
    - 🔢 This is segment {segment_num} of {total_segments}
    - 🗣️ This is a {'monologue' if num_speakers == 1 else 'conversation'}
    - 👋 Only include greetings and introductions if this is segment 1
    - 📜 Base responses strictly on the document context if available
    - 🔗 Use specific quotes and references from the document where relevant
    - 🔄 For previously mentioned entities:
        * 🛑 **Do NOT reintroduce them as new concepts**
        * 🔄 Reference them with phrases like *"as mentioned earlier"*, *"as we discussed previously"*, etc.
        * 🆕 **Introduce new aspects, relationships, or implications rather than repeating details**
    - 🎭 Maintain a natural conversational flow
    - 🔀 Ensure a **smooth transition** from the previous segment
    - {'🗣️ Maintain a consistent speaker voice' if num_speakers == 1 else '💬 Keep the dialogue natural and dynamic'}

    🚀 ENHANCEMENT INSTRUCTIONS:
    - 🤔 Think critically: What *new* insights, reactions, or developments can be added?
    - 🔥 Avoid predictable responses; introduce **unexpected perspectives**.
    - 🎨 If discussing abstract ideas, provide vivid examples, analogies, or stories.
    """

    if previous_summary and segment_num > 1:
        base_prompt += f"""
        
        🔄 PREVIOUS SEGMENT SUMMARY:
        {previous_summary}

        ➡️ Continue naturally from this point. Focus on advancing the discussion **rather than repeating past ideas**.
        """

    return base_prompt

def generate_segment_summary(conversation_piece):
    """
    Genererer et kort sammendrag av et samtalesegment.
    """
    client = get_openai_client()
    conversation_text = "\n".join([f"{u.speaker.name}: {u.text}" for u in conversation_piece.utterances])
    
    summary_prompt = f"""
    Summarize the key points and final context of this conversation segment. Focus on:
    1. Main topics discussed
    2. Key conclusions or insights
    3. The emotional/conversational state of the speakers
    4. The point where the conversation ended
    
    Conversation:
    {conversation_text}
    """
    
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": summary_prompt}],
        max_tokens=200
    )
    
    return completion.choices[0].message.content
