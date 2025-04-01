from moviepy import VideoFileClip
from pathlib import Path

def extract_audio_from_video(video_path, output_audio_path):
    """
    Extracts audio from a video file and saves it as an MP3.

    Args:
        video_path (str or Path): Path to the video file (e.g., .mov).
        output_audio_path (str or Path): Path to save the extracted audio (e.g., .mp3).
    """
    # Load the video file
    video = VideoFileClip(str(video_path))

    # Extract the audio
    audio = video.audio

    # Save the audio to the specified path
    audio.write_audiofile(str(output_audio_path), codec="mp3")

    # Close the video and audio clips
    audio.close()
    video.close()

# Usage
video_file = Path("shipwrecks.mov")  # Path to your .mov video file
output_audio_file = Path("shipwrecks_audio.mp3")  # Path for the extracted audio

# Extract and save the audio
extract_audio_from_video(video_file, output_audio_file)

print(f"Audio extracted and saved to {output_audio_file}")
