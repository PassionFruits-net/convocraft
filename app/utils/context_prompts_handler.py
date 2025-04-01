def get_section_contents(outline):
    """
    Extracts structured section contents for use in conversation generation.
    """
    section_contents = []
    for section in outline.sections:
        discussion_points = [dp.text for dp in section.discussion_points]
        entity_list = [entity for dp in section.discussion_points for entity in dp.entities]

        # Format the section content
        section_content = (
            f"FOCUS: {section.focus}\n"
            f"DISCUSSION POINTS:\n- " + "\n- ".join(discussion_points) + "\n"
            f"MENTIONED ENTITIES: {', '.join(set(entity_list)) if entity_list else 'None'}"
        )
        section_contents.append(section_content)

    return section_contents


def create_context_and_prompts(outline):
    """
    Generates context and structured prompts while tracking previous entities.
    """
    context = outline.context
    prompts = get_section_contents(outline)

    # Include previously mentioned entities to reinforce continuity
    previous_entities_text = ", ".join(outline.previous_entities) if outline.previous_entities else "None"

    context += f"\n\n🔹 Previously Mentioned Entities: {previous_entities_text}"

    return context, prompts

def get_section_contents_old(outline):
    section_contents = []
    for section in outline.sections:
        discussion_points = [dp.text for dp in section.discussion_points]
        section_content = f"FOCUS: {section.focus}\nDISCUSSION POINTS:\n- " + "\n- ".join(discussion_points)
        section_contents.append(section_content)
    return section_contents

def create_context_and_prompts_old(outline):
    context = outline.context
    prompts = get_section_contents(outline)
    return context, prompts