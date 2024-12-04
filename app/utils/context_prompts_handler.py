import streamlit as st

def get_section_contents(outline):
    section_contents = []
    for section in outline.sections:
        section_content = f"FOCUS: {section.focus}\nDISCUSSION POINTS:\n- " + "\n- ".join(section.discussion_points)
        section_contents.append(section_content)
    return section_contents

def create_context_and_prompts(outline):
    context = f"""{outline.context}. The speakers are {' and '.join([speaker.name for speaker in outline.speakers])}.
    {outline.speakers[0].name} is a {outline.speakers[0].role} and {outline.speakers[1].name} is a {outline.speakers[1].role}."""
    prompts = get_section_contents(outline)
    return context, prompts