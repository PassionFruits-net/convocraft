from pathlib import Path
from moviepy.editor import *

def combine_clips_with_audio(video_clips_dir, audio_file, output_file, fps=30, crossfade_duration=2):
    """
    Combines preprocessed video clips with crossfade transitions and syncs with audio.
    Args:
        video_clips_dir (Path): Directory containing preprocessed video clips.
        audio_file (str): Path to the audio file.
        output_file (str): Path to save the final video.
        fps (int): Frames per second for the output video.
        crossfade_duration (int): Duration of the crossfade effect between clips.
    """
    # Load preprocessed video clips
    video_clips = sorted(video_clips_dir.glob("*.mp4"))
    clips = [VideoFileClip(str(clip)).fadein(crossfade_duration).fadeout(crossfade_duration) for clip in video_clips]

    # Concatenate video clips with crossfade
    video = concatenate_videoclips(clips, method="compose", padding=-crossfade_duration)

    # Add audio
    audio = AudioFileClip(audio_file)
    video = video.set_audio(audio)

    # Write the final video
    video.write_videofile(
        output_file,
        codec="libx264",
        fps=fps,
        audio_codec="aac",
        threads=4,
        preset="ultrafast"
    )

if __name__ == "__main__":
    project_dir = Path("/Users/asadisaghar/Desktop/PRIVATE/Projects/PassionFruits/chatgpt_convo")
    video_clips_dir = project_dir / "preprocessed_clips"
    audio_file = project_dir / "shipwrecks_audio.mp3"
    output_file = project_dir / "shipwrecks_video_two_steps.mp4"

    from datetime import datetime
    start_time = datetime.now()
    combine_clips_with_audio(video_clips_dir, audio_file, output_file)
    end_time = datetime.now()
    print("Time taken(seconds):", (end_time - start_time).total_seconds())
    print("Time taken(minutes):", (end_time - start_time).total_seconds() / 60.)