import os
import random
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import subprocess
import speech_recognition as sr

# Step 1: Generate audio from the script
def generate_audio(script_text, output_audio_file="output_audio.mp3"):
    tts = gTTS(text=script_text, lang='en')
    tts.save(output_audio_file)
    return output_audio_file

# Step 2: Randomize and trim background clips to match audio length
def add_audio_to_video(background_clips, audio_file, output_video="final_video.mp4", output_folder="output_videos"):
    # Load the generated audio file to get its duration
    audio = AudioFileClip(audio_file)
    audio_duration = audio.duration
    
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

# Step 3: Generate subtitles
def generate_subtitles_from_audio(audio_file, script_text):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    # Recognize speech using Google Web Speech API
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return script_text  # Fallback to original script if speech recognition fails
    except sr.RequestError as e:
        return script_text  # Fallback if there's an API issue

# Step 4: Add subtitles to the video
def add_subtitles_to_video(video_file, subtitle_text, output_video_with_subs="final_with_subtitles.mp4", output_folder="output_videos"):
    video = VideoFileClip(video_file)
    
    # Create a TextClip for each line of subtitles and set its position
    text_clip = TextClip(subtitle_text, fontsize=24, color='white', font='Arial-Bold', stroke_color='black', stroke_width=1)
    text_clip = text_clip.set_position(('center', 'bottom')).set_duration(video.duration)
    
    # Overlay subtitles on the video
    video_with_subtitles = CompositeVideoClip([video, text_clip])
    
    output_path = os.path.join(output_folder, output_video_with_subs)
    
    # Write the final video with subtitles
    video_with_subtitles.write_videofile(output_path, codec="libx264", audio_codec="aac")
    return output_path

# Complete workflow with subtitles
def create_video_with_audio_and_subtitles(script_text, background_clips, output_folder="output_videos"):
    # Generate the audio from the provided script
    audio_file = generate_audio(script_text)
    
    # Add audio to the randomized and trimmed video clips
    video_file = add_audio_to_video(background_clips, audio_file, output_video="final_video.mp4", output_folder=output_folder)
    
    # Generate subtitles (use the script text for simplicity, or try to recognize from audio)
    subtitle_text = generate_subtitles_from_audio(audio_file, script_text)
    
    # Add subtitles to the final video
    video_with_subtitles = add_subtitles_to_video(video_file, subtitle_text, output_video_with_subs="final_with_subtitles.mp4", output_folder=output_folder)
    
    print(f"Video created with subtitles: {video_with_subtitles}")

# Example usage
script_text = "This is your auto-generated video. The script, audio, and video are now fully automated with subtitles."
background_clips = ["clip1.mp4", "clip2.mp4", "clip3.mp4"]  # Replace with your actual video file paths

# Specify the output folder where the video should be saved
create_video_with_audio_and_subtitles(script_text, background_clips, output_folder="my_videos")
