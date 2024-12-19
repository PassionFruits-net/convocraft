from utils.data_models import Conversation

def merge_conversation(conversation_pieces: list) -> Conversation:
    full_conversation = Conversation(utterances=[])
    for conversation in conversation_pieces:
        full_conversation.utterances.extend(conversation.utterances)
    return full_conversation
