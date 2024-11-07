from .Functionality.script_generation.script import generate_script
from .Functionality.audio_generation.audio import generate_audio
from .Functionality.video_editing.video import add_audio_to_video
from .Functionality.sub_generation.sub import add_subtitles_to_video, generate_word_level_srt, clear_folder
from .Functionality.utils.utils import ensure_folder_exists
from .Functionality.music_generation.music import add_background_music

import time

def create_video_with_audio_and_subtitles(background_clips_folder):
    # Generate the script using GPT
    script_text = generate_script()
    
    timestamp = int(time.time())

    # Generate the audio from the provided script
    audio_file = generate_audio(script_text)

    # Add audio to the randomized and trimmed video clips
    video_file = add_audio_to_video(background_clips_folder, audio_file, output_video=f"final_audio{timestamp}.mp4")

    # Generate the SRT file from the audio
    srt_file = generate_word_level_srt(audio_file)

    # Add subtitles to the final video
    video_with_subtitles = add_subtitles_to_video(video_file, srt_file, output_video_with_subs=f"final_sub{timestamp}.mp4")

    final_video_with_music = add_background_music(video_with_subtitles,  output_video_file=f"finalvid{timestamp}.mp4" )

    print(f"Final Video Created: {final_video_with_music}")

    # Clean up temporary files
    clear_folder('audio_outputs')
    clear_folder('audio_vids')
    clear_folder('transcripts')

# Example usage
if __name__ == "__main__":
    background_clips_folder = "background_clips"  # Replace with your actual folder containing clips

    # Specify the output folder where the video should be saved
    create_video_with_audio_and_subtitles(background_clips_folder)
