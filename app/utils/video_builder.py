import os
import subprocess
from . import persistence
import tempfile
import contextlib

def generate_clips_from_images(images):
    res = []
    for image in sorted(images):
        with fsspec.open(image, 'rb', cache_type='file') as inf:
            with persistence.write_persisted_file(".mp4", "wb") as outf:
                cmd = [
                    "ffmpeg", "-y",
                    "-loop", "1",
                    "-i", inf.name,
                    "-vf", "zoompan=z='zoom+0.00075':d=30*30:s=1920x1080,"
                           "fade=t=in:st=0:d=2,fade=t=out:st=28:d=2",
                    "-t", "30",
                    "-r", "30",
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    outf.path
                ]
                subprocess.run(cmd, check=True)
            res.append(outf.url)
    return res

def combine_clips_and_audio(clip_paths: list[str], audio_path: str):
    with ExitStack() as stack:
        clip_files = [stack.enter_context(fsspec.open(url, 'rb', cache_type='file'))
                      for url in lip_paths]
        clip_local_paths = [f.name for f in clip_files]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as file_list:
            for clip_path in clip_local_paths:
                file_list.write(f"file '{clip_path}'\n")

            with fsspec.open(audio_path, 'rb', cache_type='file') as audiof:
                with write_persisted_file(".mp4", "wb") as outf:
                    cmd = [
                        "ffmpeg", "-y",
                        "-safe", "0",
                        "-f", "concat",
                        "-i", file_list.name,
                        "-i", audiof.name,
                        "-c:v", "copy",
                        "-c:a", "aac",
                        "-b:a", "192k",
                        "-shortest",
                        outf.name
                    ]
                    subprocess.run(cmd, check=True)
                return outf.url
@contextlib.contextmanager
def encode(input_path):
    with tempfile.NamedTemporaryFile(suffix=".mp4") as temp:
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
            "-ar", "48000", "-ac", "2", temp.name
        ], check=True)
        yield temp.name
        
def finalize_video_with_intro_outro(
    main_video_path: str,
    intro_path: str = None,
    outro_path: str = None,
    bg_music_path: str = None
):
    with contextlib.ExitStack() as stack:
        bg_music = bg_music_path and stack.enter_context(fsspec.open(bg_music_path, 'rb', cache_type='file'))

        parts = [
            stack.enter_context(
                encode(
                    stack.enter_context(
                        fsspec.open(part, 'rb', cache_type='file')
                    ).name))
            for part in (intro_path, main_video_path, outro_path)
            if part
        ]

        # Combine video segments
        video_file_list = stack.enter_context(tempfile.NamedTemporaryFile(suffix=".txt"))
        for part in parts:
            video_file_list.write(f"file '{part}'\n")

        # FIXME: No idea how this was supposed to work really, figure it out :)
        # if bg_music:
        #     subprocess.run([
        #         "ffmpeg", "-y", "-i", "video.mp4",
        #         "-stream_loop", "-1", "-i", bg_music.name,
        #         "-filter_complex",
        #         "[1:a]volume=0.1,afade=t=in:ss=0:d=5,afade=t=out:st=8295:d=5[a1];"
        #         "[0:a][a1]amix=inputs=2:weights=1 0.3:duration=first",
        #         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        #         "combined_audio_video.mp4"
        #     ], check=True)
        #     final_input = "combined_audio_video.mp4"
        # else:
        #     final_input = main_video.name
            
        with write_persisted_file(".mp4", "wb") as outf:
            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", video_file_list.name,
                "-c:v", "libx264", "-crf", "23", "-preset", "fast",
                "-c:a", "aac", "-b:a", "192k",
                outf.name
            ], check=True)
        return outf.url
