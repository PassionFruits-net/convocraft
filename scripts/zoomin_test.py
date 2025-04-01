import math
import numpy as np
from PIL import Image
from moviepy.editor import *
from pathlib import Path

def generate_video_with_audio_optimized(images, audio_path, output_file, video_size=(1280, 720), fps=30, fade_duration=1.0):
    """
    Generates a video with images, applies zoom-in and fade-in effects, and syncs with audio.
    Optimized for performance with anti-vibration zoom.
    """
    # Load the audio file
    audio = AudioFileClip(str(audio_path))  # Ensure audio_path is a string
    audio_duration = audio.duration

    # Calculate the duration for each image
    image_duration = audio_duration / len(images)

    # Preprocess images to target size for consistent resizing
    processed_images = []
    for img_path in images:
        img = Image.open(str(img_path)).resize(video_size, Image.LANCZOS)  # Ensure img_path is a string
        processed_images.append(np.array(img))

    # Create a list to store video clips
    video_clips = []

    for img_array in processed_images:
        # Convert preprocessed image array to a clip
        img_clip = ImageClip(img_array, duration=image_duration)

        # Apply zoom-in and fade-in effects combined
        def combined_effect(get_frame, t):
            """
            Applies zoom-in and fade-in effects without vibrations.
            """
            frame = get_frame(t)
            alpha = min(1.0, t / fade_duration)  # Fade-in alpha
            zoom_factor = 1 + (0.04 * t)  # Smooth zoom factor

            # Calculate zoomed dimensions
            zoom_width = int(round(video_size[0] * zoom_factor))
            zoom_height = int(round(video_size[1] * zoom_factor))

            # Resize the frame smoothly
            img = Image.fromarray(frame).resize((zoom_width, zoom_height), Image.LANCZOS)

            # Calculate cropping to maintain center alignment
            crop_x = (zoom_width - video_size[0]) // 2
            crop_y = (zoom_height - video_size[1]) // 2

            # Crop the resized image to the original size
            cropped = img.crop((crop_x, crop_y, crop_x + video_size[0], crop_y + video_size[1]))

            # Apply fade-in by blending with a black background
            blended_frame = (np.array(cropped) * alpha).astype(np.uint8)

            return blended_frame

        img_clip = img_clip.fl(combined_effect, apply_to=['mask'])

        # Append to video clips
        video_clips.append(img_clip)

    # Concatenate all image clips
    video = concatenate_videoclips(video_clips, method="compose")

    # Set audio to the concatenated video
    video = video.set_audio(audio)

    # Write the final video to the output file
    video.write_videofile(
        str(output_file),  # Ensure output_file is a string
        codec="h264_videotoolbox",  # Use Apple's VideoToolbox for hardware acceleration
        fps=fps,
        audio_codec="aac",
        threads=4,  # Utilize multiple CPU cores
        preset="fast",  # Faster GPU preset
        ffmpeg_params=["-pix_fmt", "yuv420p", "-crf", "23"]  # Ensure compatibility and quality balance
    )

# Usage Example
project_dir = Path("/Users/asadisaghar/Desktop/PRIVATE/Projects/PassionFruits/chatgpt_convo")
image_dir = project_dir / "images"
image_paths = sorted(image_dir.glob("*.png"))[:5]  # List of image paths as PosixPath objects
audio_path = "shipwrecks_audio_trimmed.mp3"  # Ensure audio path is a PosixPath
output_video_path = project_dir / "Shipwrecks_optimized.mp4"  # Ensure output path is a PosixPath

# Generate the video
from datetime import datetime
t0 = datetime.now()
generate_video_with_audio_optimized(image_paths, audio_path, output_video_path)
t1 = datetime.now()
print(f"Video generation completed in {(t1 - t0).total_seconds()} seconds.")