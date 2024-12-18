def get_section_contents(outline):
    section_contents = []
    for section in outline.sections:
        section_content = f"FOCUS: {section.focus}\nDISCUSSION POINTS:\n- " + "\n- ".join(section.discussion_points)
        section_contents.append(section_content)
    return section_contents

def create_context_and_prompts(outline):
    context = outline.context
    prompts = get_section_contents(outline)
    return context, prompts