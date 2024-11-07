import os
import random
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

def add_audio_to_video(background_clips_folder, audio_file, output_video="final_video.mp4", output_folder="output_videos"):
    # Load the generated audio file to get its duration
    audio = AudioFileClip(audio_file)
    audio_duration = audio.duration

    # Load all video files from the specified folder
    background_clips = [os.path.join(background_clips_folder, f) for f in os.listdir(background_clips_folder) if f.endswith(".mp4")]

    # Shuffle the background clips for random order
    random.shuffle(background_clips)

    clips = []
    total_duration = 0

    # Loop through background clips and trim them to fit audio duration
    for clip_file in background_clips:
        clip = VideoFileClip(clip_file)
        clip_duration = clip.duration

        if total_duration + clip_duration > audio_duration:
            # Trim the clip to match the remaining duration
            remaining_duration = audio_duration - total_duration
            clip = clip.subclip(0, remaining_duration)
            clips.append(clip)
            break
        else:
            clips.append(clip)
            total_duration += clip_duration

    # Concatenate the video clips
    final_clip = concatenate_videoclips(clips)

    # Set the generated audio as the video’s audio
    final_clip = final_clip.set_audio(audio)

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_path = os.path.join(output_folder, output_video)

    # Write the final video file
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    return output_path
