# music.py

import os
import random
import time
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeAudioClip,
    concatenate_audioclips
)

def add_background_music(
    video_file,
    output_video_file,
    music_folder='music_clips',
    output_folder="final_videos"
):
    """
    Adds background music to a video by selecting a random music clip from the specified folder,
    trimming or looping it to match the video's duration, and combining it with the video's audio.

    Parameters:
    - video_file (str): Path to the input video file that already has text, audio, and subtitles.
    - output_video_file (str): Filename for the output video file with background music.
    - music_folder (str): Path to the folder containing music clips.
    - output_folder (str): Path to the folder where the final video will be saved.

    Returns:
    - str: Path to the output video file with background music, or None if an error occurs.
    """

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Generate timestamp for unique filenames if needed
    timestamp = int(time.time())

    # Full path for the output video file
    output_path = os.path.join(output_folder, output_video_file)

    # Load the video
    video = VideoFileClip(video_file)
    video_duration = video.duration

    # Get a list of all music files in the music_folder
    music_files = [
        os.path.join(music_folder, f)
        for f in os.listdir(music_folder)
        if f.lower().endswith(('.mp3', '.wav', '.aac', '.m4a', '.ogg'))
    ]

    if not music_files:
        print(f"No music files found in {music_folder}.")
        return None

    # Randomly select a music file
    selected_music_file = random.choice(music_files)
    print(f"Selected background music: {selected_music_file}")

    # Load the background music
    background_music = AudioFileClip(selected_music_file)
    music_duration = background_music.duration

    # Adjust background music duration to match the video duration
    # Check if the music clip is longer than the video first
    if music_duration >= video_duration:
        # Cut the music to match the video's duration
        bg_music = background_music.subclip(0, video_duration)
    else:
        # Loop the music to match the video's duration
        loops = int(video_duration // music_duration) + 1
        music_clips = [background_music] * loops
        concatenated_music = concatenate_audioclips(music_clips)
        bg_music = concatenated_music.subclip(0, video_duration)

    # Reduce the volume of the background music
    bg_music = bg_music.volumex(0.2)  # Adjust volume level as needed

    # If the video has existing audio, combine it with the background music
    if video.audio:
        # Adjust the volume of the video's audio if necessary
        video_audio = video.audio.volumex(1.0)  # Adjust volume level as needed

        # Combine the video's audio and the background music
        final_audio = CompositeAudioClip([video_audio, bg_music])
    else:
        # Use only the background music
        final_audio = bg_music

    # Set the combined audio to the video clip
    final_video = video.set_audio(final_audio)

    # Write the final video to the output file
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)

    # Close the clips to release resources
    video.close()
    background_music.close()
    if video.audio:
        video_audio.close()
    bg_music.close()
    final_audio.close()
    final_video.close()

    print(f"Final video saved to {output_path}")
    return output_path
