import os
import openai
from typing import List
from PIL import Image
from io import BytesIO
import base64

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_images_from_plan(image_prompts: List[str], output_dir: str) -> List[str]:
    """
    Generate one image per prompt using DALL·E and save them as JPGs.
    Returns a list of saved image file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    image_paths = []

    for idx, prompt in enumerate(image_prompts, 1):
        print(f"🎨 Generating image for: {prompt}")

        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1792x1024",  # DALL·E high-res
                response_format="b64_json"
            )

            image_data = response["data"][0]["b64_json"]
            image = Image.open(BytesIO(base64.b64decode(image_data)))
            filename = os.path.join(output_dir, f"frame_{idx:03}.jpg")
            image.save(filename, format="JPEG")
            image_paths.append(filename)

        except Exception as e:
            print(f"❌ Error generating image for step {idx}: {e}")

    return image_paths
