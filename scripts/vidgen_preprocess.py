import os
from pathlib import Path

def preprocess_images_with_ffmpeg(image_dir, output_dir, video_size=(1280, 720), duration_range=(300, 420), fps=30):
    """
    Preprocess images into video clips with zoom and panning using FFmpeg.
    Args:
        image_dir (Path): Directory containing input images.
        output_dir (Path): Directory to save preprocessed video clips.
        video_size (tuple): Resolution of the output video (width, height).
        duration_range (tuple): Duration range (min, max) in seconds for each clip.
        fps (int): Frames per second for the output video.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    images = sorted(image_dir.glob("*.*"))[:5]  # Sort images for order
    for i, image_path in enumerate(images):
        output_file = output_dir / f"{image_path.stem}_clip.mp4"
        duration = duration_range[0] + (i % (duration_range[1] - duration_range[0]))  # Alternate durations

        # Generate FFmpeg command for zoom + pan
        zoom_speed = 1 / (fps * duration)  # Smooth zoom over the duration
        command = (
            f"ffmpeg -loop 1 -i {image_path} "
            f"-vf \"zoompan=z='zoom+{zoom_speed:.8f}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={video_size[0]}x{video_size[1]}\" "
            f"-t {duration} -r {fps} -pix_fmt yuv420p {output_file}"
        )
        os.system(command)
        print(f"Preprocessed video created: {output_file}")

if __name__ == "__main__":
    project_dir = Path("/Users/asadisaghar/Desktop/PRIVATE/Projects/PassionFruits/chatgpt_convo")
    image_dir = project_dir / "images"
    output_dir = project_dir / "preprocessed_clips"
    preprocess_images_with_ffmpeg(image_dir, output_dir)
