from script_generation.script import generate_script
from audio_generation.audio import generate_audio
from video_editing.video import add_audio_to_video
from sub_generation.sub import add_subtitles_to_video
from utils.utils import ensure_folder_exists

i = 0

def create_video_with_audio_and_subtitles(background_clips_folder):
    # Generate the script using GPT
    script_text = generate_script()

    # Generate the audio from the provided script
    audio_file = generate_audio(script_text)

    # Add audio to the randomized and trimmed video clips
    video_file = add_audio_to_video(background_clips_folder, audio_file, output_video=f"final_audio{i + 1}.mp4")

    # Add subtitles to the final video
    video_with_subtitles = add_subtitles_to_video(video_file, script_text, output_video_with_subs=f"final{i+1}.mp4")

    print(f"Video created with subtitles: {video_with_subtitles}")

# Example usage
if __name__ == "__main__":
    background_clips_folder = "background_clips"  # Replace with your actual folder containing clips

    # Specify the output folder where the video should be saved
    create_video_with_audio_and_subtitles(background_clips_folder)
