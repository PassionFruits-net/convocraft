from utils.llm_calls import fetch_conversation_responses

def augment_prompt_with_retrieval(query, retrieved_chunks):
    """
    Combines user query with retrieved document chunks to create an augmented prompt.
    """
    context = "\n\n".join([chunk for chunk, _ in retrieved_chunks])
    prompt = f"Relevant Context:\n{context}\n\nUser Query:\n{query}"
    return prompt

def rag_query(query, vector_store, model="gpt-4"):
    """
    Executes a Retrieval-Augmented Generation query.
    """
    retrieved_chunks = vector_store.query(query)
    augmented_prompt = augment_prompt_with_retrieval(query, retrieved_chunks)
    response = fetch_conversation_responses(augmented_prompt, [query], model=model)
    return response
