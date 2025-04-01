import math
import numpy as np
from PIL import Image
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
from moviepy.video.fx import Resize
from pathlib import Path


def zoom_in_effect(get_frame, t, zoom_ratio=0.04):
    """
    Custom zoom-in effect applied frame by frame.
    Args:
        get_frame: Frame-fetching function provided by MoviePy.
        t: Current timestamp (in seconds).
        zoom_ratio: Speed of the zoom effect.
    Returns:
        Transformed frame with a zoom-in effect.
    """
    # Get the current frame as an image array
    frame = get_frame(t)
    img = Image.fromarray(frame)

    # Calculate the new size based on zoom ratio
    base_size = img.size
    new_size = [
        math.ceil(base_size[0] * (1 + zoom_ratio * t)),
        math.ceil(base_size[1] * (1 + zoom_ratio * t)),
    ]

    # Ensure dimensions are even
    new_size[0] += new_size[0] % 2
    new_size[1] += new_size[1] % 2

    # Resize the image to the new size
    img = img.resize(new_size, Image.LANCZOS)

    # Calculate cropping dimensions
    x = (new_size[0] - base_size[0]) // 2
    y = (new_size[1] - base_size[1]) // 2

    # Crop and resize back to the original size
    img = img.crop([x, y, new_size[0] - x, new_size[1] - y]).resize(base_size, Image.LANCZOS)

    # Convert back to numpy array
    return np.array(img)


def fade_in_effect(clip, duration):
    """
    Adds a custom fade-in effect to a clip by gradually increasing opacity.
    Args:
        clip: The video clip to which the fade-in effect is applied.
        duration: Duration of the fade-in effect (in seconds).
    Returns:
        A video clip with the fade-in effect applied.
    """
    def fadein(get_frame, t):
        alpha = min(1, t / duration)  # Linearly increase opacity
        frame = get_frame(t)
        return (frame * alpha).astype('uint8')

    return clip.transform(fadein)


def generate_video_with_audio(images, audio_path, output_file, video_size=(1280, 720), fps=30, fade_duration=1.0):
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
        img_clip = img_clip.with_effects([Resize(width=video_size[0], height=video_size[1])])

        # Apply the zoom-in effect
        # img_clip = img_clip.transform(lambda gf, t: zoom_in_effect(gf, t))

        # Apply fade-in effect
        img_clip = fade_in_effect(img_clip, fade_duration)

        # Append to the list of video clips
        video_clips.append(img_clip)

    # Concatenate all image clips with crossfade between them
    video = concatenate_videoclips(video_clips, method="compose", padding=-fade_duration)

    # Set the audio to the concatenated video
    video = video.with_audio(audio)

    # Write the final video to the output file
    video.write_videofile(output_file, codec="libx264", fps=fps, audio_codec="aac")


# Usage
project_dir = Path("/Users/asadisaghar/Desktop/PRIVATE/Projects/PassionFruits/chatgpt_convo")
image_dir = project_dir / "generated_images"
image_paths = sorted(image_dir.glob("*.png"))
audio_path = "shipwrecks_audio.mp3"
output_video_path = project_dir / "Shipwrecks_30sec_no_zoomin.mp4"

generate_video_with_audio(image_paths, audio_path, output_video_path)