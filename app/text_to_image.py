import os
import time
import streamlit as st
from multiprocessing import Process, Manager
from utils.llm_calls import generate_images_with_dalle
from multiprocessing import set_start_method

# Ensure correct multiprocessing start method for MacOS
set_start_method("fork", force=True)

# Initialize shared dictionaries
manager = Manager()
results_dict = manager.dict()  # Shared dictionary for generated images
stop_signal = manager.dict({"abort": False})  # Shared stop signal


def generate_images_in_process(prompts, stop_signal, api_key, results_dict):
    """
    Generate images in a separate process.

    Args:
        prompts (list): List of prompts to generate images for.
        stop_signal (dict): Shared dictionary to monitor stopping.
        api_key (str): OpenAI API key.
        results_dict (dict): Shared dictionary to store generated images.
    """
    for i, prompt in enumerate(prompts):
        if stop_signal.get("abort"):
            results_dict[prompt] = {"status": "aborted"}
            break
        try:
            generated_images, image_urls = generate_images_with_dalle([prompt], stop_signal, api_key)
            for ((prompt, image_data), image_url) in zip(generated_images, image_urls):
                if image_data:
                    results_dict[prompt] = {"status": "success", "image_data": image_data, "image_url": image_url}
                else:
                    results_dict[prompt] = {"status": "failed"}
        except Exception as e:
            results_dict[prompt] = {"status": "error", "error": str(e)}


def render_image_generation_section():
    if "outline" not in st.session_state:
        st.info("Please generate/upload an outline first to enable conversation/image generation.")
        return

    st.header("🎨 Image Generation")
    discussion_points = [section.discussion_points for section in st.session_state["outline"].sections]
    prompts = [[sdp.image_prompts for sdp in section_discussion_points] for section_discussion_points in discussion_points]
    # Flatten list of lists and remove None values
    prompts = [p for sublist in prompts for p_list in sublist if p_list for p in p_list]
    selected_prompts = st.multiselect(
        "Select prompts to generate images for (or select all):",
        options=prompts,
        default=prompts
    )

    if st.button("Generate Images"):
        if selected_prompts:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                st.error("Missing OpenAI API Key.")
                return

            manager = Manager()
            results_dict = manager.dict()
            stop_signal = manager.dict({"abort": False})

            process = Process(
                target=generate_images_in_process,
                args=(selected_prompts, stop_signal, api_key, results_dict)
            )
            process.start()

            # Monitor results and update status dynamically
            status_placeholder = st.empty()
            while process.is_alive():
                status_message = []
                for prompt, result in results_dict.items():
                    if result["status"] == "success":
                        status_message.append(f"✅ {prompt}: Completed")
                    elif result["status"] == "failed":
                        status_message.append(f"❌ {prompt}: Failed")
                    elif result["status"] == "error":
                        status_message.append(f"⚠️ {prompt}: Error - {result['error']}")
                # Dynamically update the status placeholder
                status_placeholder.markdown("\n".join(status_message))
                # Wait before checking again
                time.sleep(1)

            process.join()  # Wait for the process to finish

            for prompt, result in results_dict.items():
                if result["status"] == "success":
                    st.image(result["image_data"], caption=f"Prompt: {prompt}", use_container_width=True)
                    st.download_button(
                        label="Download Image",
                        data=result["image_data"],
                        file_name=f"{prompt}.png",
                        mime="image/png"
                    )
        else:
            st.warning("Please select at least one prompt.")