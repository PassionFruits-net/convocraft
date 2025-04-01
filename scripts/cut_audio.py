from moviepy import AudioFileClip

def cut_mp3(input_audio_path, output_audio_path, start_time=0, end_time=None):
    """
    Cuts an MP3 file to the specified timestamp and saves the output.

    Args:
        input_audio_path (str): Path to the input MP3 file.
        output_audio_path (str): Path to save the trimmed MP3 file.
        start_time (float): Start time in seconds (default is 0).
        end_time (float): End time in seconds (if None, cuts until the end).
    """
    # Load the audio file
    audio = AudioFileClip(input_audio_path)

    # Trim the audio to the specified timestamps
    trimmed_audio = audio.subclipped(start_time, end_time)

    # Write the trimmed audio to a new file
    trimmed_audio.write_audiofile(output_audio_path, codec="mp3")

    # Close the audio clip
    audio.close()
    trimmed_audio.close()

# Usage
input_mp3 = "shipwrecks_audio.mp3"  # Path to your input MP3 file
output_mp3 = "shipwrecks_audio_trimmed.mp3"  # Path to save the trimmed audio
start = 0  # Start time in seconds
end = 196    # End time in seconds

cut_mp3(input_mp3, output_mp3, start_time=start, end_time=end)
print(f"Trimmed audio saved to {output_mp3}")
