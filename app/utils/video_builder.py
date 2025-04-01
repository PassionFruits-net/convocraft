import os
import subprocess

def generate_clips_from_images(image_dir: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    images = sorted([f for f in os.listdir(image_dir) if f.lower().endswith(".jpg")])
    
    for image in images:
        name = os.path.splitext(image)[0]
        input_path = os.path.join(image_dir, image)
        output_path = os.path.join(output_dir, f"{name}.mp4")

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", input_path,
            "-vf", "zoompan=z='zoom+0.00075':d=30*30:s=1920x1080,"
                   "fade=t=in:st=0:d=2,fade=t=out:st=28:d=2",
            "-t", "30",
            "-r", "30",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            output_path
        ]
        subprocess.run(cmd, check=True)

def combine_clips_and_audio(clips_dir: str, audio_path: str, output_path: str):
    list_file = os.path.join(clips_dir, "file_list.txt")

    with open(list_file, "w") as f:
        for filename in sorted(os.listdir(clips_dir)):
            if filename.endswith(".mp4"):
                clip_path = os.path.join(clips_dir, filename)
                # Write relative or properly escaped path
                f.write(f"file '{clip_path}'\n")

    # Add input checks
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    if not os.path.exists(list_file):
        raise FileNotFoundError(f"FFmpeg file list not found: {list_file}")

    cmd = [
        "ffmpeg", "-y",
        "-safe", "0",
        "-f", "concat",
        "-i", list_file,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_path
    ]

    subprocess.run(cmd, check=True)

def finalize_video_with_intro_outro(
    main_video_path: str,
    output_path: str,
    intro_path: str = None,
    outro_path: str = None,
    bg_music_path: str = None
):
    def encode(input_path, output_path):
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
            "-ar", "48000", "-ac", "2", output_path
        ], check=True)

    parts = []

    if intro_path:
        encode(intro_path, "intro.mp4")
        parts.append("intro.mp4")

    encode(main_video_path, "video.mp4")
    parts.append("video.mp4")

    if outro_path:
        encode(outro_path, "outro.mp4")
        parts.append("outro.mp4")

    # Combine video segments
    with open("video_file_list.txt", "w") as f:
        for part in parts:
            f.write(f"file '{part}'\n")

    if bg_music_path:
        subprocess.run([
            "ffmpeg", "-y", "-i", "video.mp4",
            "-stream_loop", "-1", "-i", bg_music_path,
            "-filter_complex",
            "[1:a]volume=0.1,afade=t=in:ss=0:d=5,afade=t=out:st=8295:d=5[a1];"
            "[0:a][a1]amix=inputs=2:weights=1 0.3:duration=first",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "combined_audio_video.mp4"
        ], check=True)
        final_input = "combined_audio_video.mp4"
    else:
        final_input = "video.mp4"

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", "video_file_list.txt",
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        output_path
    ], check=True)
