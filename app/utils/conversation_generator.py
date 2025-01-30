from utils.data_models import Conversation
from utils.llm_calls import get_openai_client

def merge_conversation(conversation_pieces: list) -> Conversation:
    full_conversation = Conversation(utterances=[])
    for conversation in conversation_pieces:
        full_conversation.utterances.extend(conversation.utterances)
    return full_conversation

def create_segment_prompt(context, prompt, segment_info, previous_summary=None):
    """
    Generate a prompt for a specific segment of the conversation.
    """
    segment_num = segment_info["current_split"] + 1
    total_segments = segment_info["total_splits"]
    
    base_prompt = f"""
    SEGMENT {segment_num} OF {total_segments}

    CONTEXT:
    {context}

    SECTION CONTENT:
    {prompt}

    INSTRUCTIONS:
    - This is segment {segment_num} of {total_segments}
    - Do NOT include greetings or introductions unless this is segment 1
    - Maintain natural conversation flow
    - Ensure smooth transition from previous segment
    - Participants must NOT call each other by name, unless explicitly stated in the context
    """
    
    if previous_summary and segment_num > 1:
        base_prompt += f"""
        
        PREVIOUS SEGMENT SUMMARY:
        {previous_summary}
        
        Continue the conversation naturally from this point.
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
        model="gpt-4",
        messages=[{"role": "user", "content": summary_prompt}],
        max_tokens=200
    )
    
    return completion.choices[0].message.content
