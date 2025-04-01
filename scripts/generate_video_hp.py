import math
import numpy as np
from PIL import Image
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
from pathlib import Path


def zoom_in_effect_dynamic(clip, zoom_ratio=0.04, duration=None):
    """
    Applies a dynamic zoom-in effect, where the zoom level increases over time.
    Args:
        clip: The input clip to which the zoom effect will be applied.
        zoom_ratio: The speed of the zoom-in effect (e.g., 0.04 for 4% per second).
        duration: The duration of the zoom effect (in seconds). If None, uses the clip's duration.
    Returns:
        A video or image clip with the zoom-in effect applied.
    """
    if duration is None:
        duration = clip.duration  # Use the clip's total duration if not specified.

    def dynamic_zoom(get_frame, t):
        frame = get_frame(t)
        height, width, _ = frame.shape
        zoom_factor = 1 + zoom_ratio * t  # Zoom level increases with time
        new_width = int(width * zoom_factor)
        new_height = int(height * zoom_factor)

        # Resize and crop to maintain original dimensions
        img = Image.fromarray(frame).resize((new_width, new_height), Image.LANCZOS)
        crop_x = (new_width - width) // 2
        crop_y = (new_height - height) // 2
        img = img.crop((crop_x, crop_y, crop_x + width, crop_y + height))
        return np.array(img)

    return clip.transform(dynamic_zoom)


def fade_in_effect(clip, duration):
    """
    Adds a fade-in effect to a video clip by linearly increasing the opacity over time.
    Args:
        clip: The video clip to which the fade-in effect is applied.
        duration: Duration of the fade-in effect (in seconds).
    Returns:
        A video clip with the fade-in effect applied.
    """
    def fadein(get_frame, t):
        frame = get_frame(t)
        alpha = min(1.0, t / duration)  # Linearly increase alpha from 0 to 1
        return (frame * alpha).astype(np.uint8)

    return clip.transform(fadein)


def generate_video_with_audio(images, audio_path, output_file, video_size=(1280, 720), fps=24, fade_duration=1.0):
    """
    Generates a video with images, applies zoom-in and fade-in effects, and syncs with audio.
    Args:
        images: List of image file paths.
        audio_path: Path to the audio file.
        output_file: Output video file path.
        video_size: Tuple specifying the size of the video (width, height).
        fps: Frames per second for the output video.
        fade_duration: Duration of fade-in between consecutive clips (in seconds).
    """
    # Load the audio file
    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration

    # Calculate the duration for each image
    image_duration = audio_duration / len(images)

    # Create a list to store the video clips
    video_clips = []

    for img_path in images:
        # Load the image
        img_clip = ImageClip(str(img_path), duration=image_duration)
        
        # Resize the image to the specified video size
        img_clip = img_clip.resized(video_size)

        # Apply the zoom-in effect
        img_clip = zoom_in_effect_dynamic(img_clip)

        # Apply fade-in effect
        img_clip = fade_in_effect(img_clip, fade_duration)

        # Append to the list of video clips
        video_clips.append(img_clip)

    # Concatenate all image clips
    video = concatenate_videoclips(video_clips, method="compose")

    # Set the audio to the concatenated video
    video = video.with_audio(audio)

    # Write the final video to the output file
    video.write_videofile(
        output_file,
        codec="libx264",
        fps=fps,
        audio_codec="aac",
        threads=4,  # Utilize multiple CPU cores
        preset="ultrafast",  # Speed up encoding
        ffmpeg_params=["-crf", "23"]  # Balance quality and compression
    )


# Usage
project_dir = Path("/Users/asadisaghar/Desktop/PRIVATE/Projects/PassionFruits/chatgpt_convo")
image_dir = project_dir / "images"
image_paths = sorted(image_dir.glob("*.png"))
audio_path = project_dir / "shipwrecks_audio.mp3"
output_video_path = project_dir / "Shipwrecks_with_zoomin.mp4"

generate_video_with_audio(image_paths, audio_path, output_video_path)
