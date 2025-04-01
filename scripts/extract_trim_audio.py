from moviepy.video.io.VideoFileClip import VideoFileClip

def extract_and_trim_audio(input_mov_path, output_mp3_path, t0, t1):
    """
    Extracts audio from a .mov file, trims it, and saves it as an .mp3 file.
    
    Args:
        input_mov_path (str): Path to the input .mov file.
        output_mp3_path (str): Path to save the trimmed .mp3 file.
        t0 (float): Start time in seconds for the trim.
        t1 (float): End time in seconds for the trim.
    """
    try:
        # Load the .mov file
        with VideoFileClip(input_mov_path) as video_clip:
            # Extract the audio
            audio_clip = video_clip.audio
            if audio_clip is None:
                raise ValueError("The provided .mov file does not contain any audio.")
            
            # Trim the audio
            trimmed_audio = audio_clip.subclipped(t0, t1)
            
            # Write the trimmed audio to an mp3 file
            trimmed_audio.write_audiofile(output_mp3_path, codec="libmp3lame")
            
            # Close the trimmed audio clip
            trimmed_audio.close()
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
input_mov = "Shipwrecks.mov"  # Replace with your .mov file path
output_mp3 = "shipwrecks_audio_trimmed.mp3"  # Replace with desired output .mp3 file path
start_time = 0  # Replace with your desired start time in seconds
end_time = 196  # Replace with your desired end time in seconds

extract_and_trim_audio(input_mov, output_mp3, start_time, end_time)
