import os
import openai
from typing import List

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_image_prompts_from_steps(theme: str, plan_steps: List[str]) -> List[str]:
    """
    Use GPT to transform plan steps + theme into image prompts suitable for DALL·E.
    """
    plan_lines = "\n".join([f"{i+1}. {step}" for i, step in enumerate(plan_steps)])
    
    prompt = f"""
You are helping create illustrations for a story video with the theme "{theme}".
Here are the main points of each paragraph:

{plan_lines}

For each point, generate a short, vivid image prompt suitable for DALL·E.
Make the prompts visual, detailed, and imaginative — 1–2 sentences each.
Style and atmosphere should match the theme "{theme}".
Return the prompts as a numbered list.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=1000
    )

    raw_text = response["choices"][0]["message"]["content"]
    
    # Extract just the lines starting with numbers (e.g. 1. ...)
    image_prompts = [line.partition(".")[2].strip() for line in raw_text.splitlines() if line.strip().startswith(tuple("123456789"))]
    
    return image_prompts
