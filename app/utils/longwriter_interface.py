import os
import requests
from typing import List, Tuple
import json
from datetime import datetime

# Load templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLAN_PATH = os.path.join(BASE_DIR, "..", "agentwrite", "prompts", "plan.txt")
WRITE_PATH = os.path.join(BASE_DIR, "..", "agentwrite", "prompts", "write.txt")

with open(PLAN_PATH, "r", encoding="utf-8") as f:
    PLAN_TEMPLATE = f.read()

with open(WRITE_PATH, "r", encoding="utf-8") as f:
    WRITE_TEMPLATE = f.read()

# OpenAI setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GPT_MODEL = "gpt-4o-2024-05-13"

def call_openai_api(prompt: str, max_tokens: int = 1024, temperature: float = 1.0) -> str:
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    payload = {
        "model": GPT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    for _ in range(5):
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=600
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Retrying after error: {e}")
    return "Error: Failed after retries"

def generate_paragraph_plan(instruction: str) -> List[str]:
    prompt = PLAN_TEMPLATE.replace("$INST$", instruction)
    response = call_openai_api(prompt)
    return [line.strip() for line in response.split("\n") if line.strip()]

def generate_longwriter_output(instruction: str) -> Tuple[str, List[str]]:
    """
    Returns:
        - full generated story (str)
        - list of plan steps used (List[str])
    """
    plan_steps = generate_paragraph_plan(instruction)
    full_text = ""
    plan_str = "\n".join(plan_steps)

    for step in plan_steps:
        prompt = (
            WRITE_TEMPLATE
            .replace("$INST$", instruction)
            .replace("$PLAN$", plan_str.strip())
            .replace("$TEXT$", full_text.strip())
            .replace("$STEP$", step)
        )
        paragraph = call_openai_api(prompt)
        full_text += paragraph.strip() + "\n\n"

    return full_text.strip(), plan_steps


def save_generation_to_jsonl(instruction: str, plan_steps: List[str], story: str, output_file: str = "longwriter_outputs.jsonl"):
    """
    Appends the instruction, plan, and story to a .jsonl file for replay.
    """
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "instruction": instruction,
        "plan_steps": plan_steps,
        "story": story
    }

    with open(output_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
