from moviepy import VideoFileClip

def extract_and_trim_audio(video_path, output_audio_path, start_time=0, end_time=None):
    """
    Extracts and trims audio from a video file and saves it as an MP3.

    Args:
        video_path (str): Path to the video file (e.g., .mov).
        output_audio_path (str): Path to save the trimmed audio (e.g., .mp3).
        start_time (float): Start time in seconds (default is 0).
        end_time (float): End time in seconds (if None, cuts until the end).
    """
    # Load the video file
    video = VideoFileClip(video_path)

    # Extract the audio
    audio = video.audio

    # Trim the audio
    trimmed_audio = audio.subclipped(start_time, end_time)

    # Save the trimmed audio
    trimmed_audio.write_audiofile(output_audio_path, codec="mp3")

    # Close resources
    audio.close()
    video.close()
    trimmed_audio.close()

# Usage
video_file = "shipwrecks.mov"  # Path to your video file
output_audio = "shipwrecks_audio_trimmed.mp3"  # Path for the trimmed audio
start = 0  # Start time in seconds
end = 196  # End time in seconds

extract_and_trim_audio(video_file, output_audio, start_time=start, end_time=end)
print(f"Trimmed audio saved to {output_audio}")
