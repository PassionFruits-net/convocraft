import re

def extract_participant_names(text):
    """
    Extract participant names from the text using a regex pattern.
    """
    pattern = r"\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b"  # Matches capitalized names
    return re.findall(pattern, text)

def update_context_with_names(context, names):
    """
    Update the context to include the participant names.
    """
    updated_context = context
    for i, name in enumerate(names, start=1):
        if f"Participant{i}" in context:
            updated_context = updated_context.replace(f"Participant{i}", name)
    return updated_context

def update_prompts_with_names(prompts, names):
    """
    Update the prompts to include the participant names.
    """
    updated_prompts = []
    for prompt in prompts:
        updated_prompt = prompt
        for i, name in enumerate(names, start=1):
            if f"Participant{i}" in prompt:
                updated_prompt = updated_prompt.replace(f"Participant{i}", name)
        updated_prompts.append(updated_prompt)
    return updated_prompts
