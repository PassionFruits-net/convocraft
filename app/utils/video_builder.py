import os
import subprocess
import fsspec
from . import persistence
import tempfile
import contextlib
import adlfs
import shutil
from dotenv import load_dotenv
from contextlib import ExitStack


def normalize_file_url(path: str) -> str:
    path = str(path)
    if path.startswith("file://"):
        return path.replace("file://", "")
    elif path.startswith("file:/"):
        return path.replace("file:/", "/")
    return path

def generate_clips_from_images(images):
    load_dotenv()
    
    # Initialize the AzureBlobFileSystem once
    fs = adlfs.AzureBlobFileSystem(
        account_name=os.getenv("AZURE_STORAGE_ACCOUNT_NAME"),
        account_key=os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
    )

    res = []

    for image in sorted(images, key=str):
        print("IMAGE:", image)

        # Extract container and blob path from az://... URI
        stripped = str(image).replace("az://", "")
        container, blob_path = stripped.split("/", 1)
        full_path = f"{container}/{blob_path}"

        print("Container:", container)
        print("Blob path:", blob_path)
        print("IMAGE EXISTS?", fs.exists(full_path))

        if not fs.exists(full_path):
            raise FileNotFoundError(f"Blob does not exist: {full_path}")

        # Read image into local temp file
        with fs.open(full_path, 'rb') as inf:
            image_bytes = inf.read()
            if not image_bytes:
                raise ValueError(f"Failed to read image from {full_path}")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
                tmp_img.write(image_bytes)
                tmp_img.flush()
                tmp_img_path = tmp_img.name

        print("TEMP FILE EXISTS?", os.path.exists(tmp_img_path))
        print("SIZE:", os.path.getsize(tmp_img_path))

        # Generate video with ffmpeg
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_outf:
            tmp_outf_path = tmp_outf.name
        
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", tmp_img_path,
            "-vf", "zoompan=z='zoom+0.00075':d=30*30:s=1920x1080,"
                "fade=t=in:st=0:d=2,fade=t=out:st=28:d=2",
            "-t", "30",
            "-r", "30",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-color_range", "2",
            tmp_outf_path
        ]
        subprocess.run(cmd, check=True)

        # Persist and get URL:
        url = persistence.persist_file(tmp_outf_path, name="clip.mp4")
        res.append(url)

        os.unlink(tmp_outf_path)

    return res


def combine_clips_and_audio(clip_paths: list[str], audio_path: str):
    clip_local_paths = []

    try:
        for url in clip_paths:
            with fsspec.open(url, 'rb') as remote_f:
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                shutil.copyfileobj(remote_f, tmp)
                tmp.flush()
                clip_local_paths.append(tmp.name)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w") as file_list:
            for path in clip_local_paths:
                file_list.write(f"file '{path}'\n")
            file_list.flush()

            with fsspec.open(normalize_file_url(audio_path), 'rb') as audiof:
                tmp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                shutil.copyfileobj(audiof, tmp_audio)
                tmp_audio.flush()

                with persistence.write_persisted_file(".mp4", "wb") as outf:
                    cmd = [
                        "ffmpeg", "-y",
                        "-safe", "0",
                        "-f", "concat",
                        "-i", file_list.name,
                        "-i", tmp_audio.name,
                        "-c:v", "copy",
                        "-c:a", "aac",
                        "-b:a", "192k",
                        "-shortest",
                        outf.name
                    ]
                    subprocess.run(cmd, check=True)

                return outf.url

    finally:
        # Clean up temp clip and audio files
        for f in clip_local_paths:
            os.unlink(f)
        if 'tmp_audio' in locals():
            os.unlink(tmp_audio.name)
        if 'file_list' in locals():
            os.unlink(file_list.name)


@contextlib.contextmanager
def encode(input_path):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp:
        temp_path = temp.name

    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-ar", "48000", "-ac", "2", temp_path
    ], check=True)

    try:
        yield temp_path
    finally:
        os.unlink(temp_path)
        
def finalize_video_with_intro_outro(
    main_video_path: str,
    intro_path: str = None,
    outro_path: str = None,
    bg_music_path: str = None
):
    print("MAIN VIDEO:", main_video_path)
    print("INTRO VIDEO:", intro_path)
    print("OUTRO VIDEO:", outro_path)
    print("BG MUSIC:", bg_music_path)
    with contextlib.ExitStack() as stack:
        temp_files = []

        # Optional: download bg music
        bg_music_local = None
        if bg_music_path:
            with fsspec.open(bg_music_path, 'rb') as remote_audio:
                tmp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                shutil.copyfileobj(remote_audio, tmp_audio)
                tmp_audio.flush()
                bg_music_local = tmp_audio.name
                temp_files.append(bg_music_local)

        # Collect all parts (intro, main, outro)
        video_parts = []
        for part_path in (intro_path, main_video_path, outro_path):
            if not part_path:
                continue
            print("PART:", part_path)
            # Download part to temp file
            with fsspec.open(part_path, 'rb') as remote_f:
                tmp_in = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                shutil.copyfileobj(remote_f, tmp_in)
                tmp_in.flush()
                tmp_in_path = tmp_in.name
                temp_files.append(tmp_in_path)

            # Encode and keep output file path
            encoded_path = stack.enter_context(encode(tmp_in_path))
            video_parts.append(encoded_path)

        # Create concat list file
        concat_list_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w")
        for path in video_parts:
            concat_list_file.write(f"file '{path}'\n")
        concat_list_file.flush()
        temp_files.append(concat_list_file.name)

        # Combine parts with optional audio
        with persistence.write_persisted_file(".mp4", "wb") as outf:
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", concat_list_file.name,
                "-c:v", "libx264", "-crf", "23", "-preset", "fast",
                "-c:a", "aac", "-b:a", "192k"
            ]
            if bg_music_local:
                cmd += ["-i", bg_music_local, "-shortest"]
            cmd += [outf.name]

            subprocess.run(cmd, check=True)

        # Clean up temp files
        for path in temp_files:
            try:
                os.unlink(path)
            except FileNotFoundError:
                pass  # already cleaned

        return outf.url