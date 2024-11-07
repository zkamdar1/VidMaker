import os
import re
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from openai import OpenAI

client = OpenAI()

# Set your OpenAI API key
client.api_key = os.getenv("OPENAI_API_KEY")

# Function to generate subtitles (SRT) using Whisper
def generate_srt_from_audio(audio_file_path, transcripts_folder="transcripts", output_srt_filename="transcript.srt"):
    # Ensure the output folder for transcripts exists
    if not os.path.exists(transcripts_folder):
        os.makedirs(transcripts_folder)

    # Generate full path for the output SRT file
    output_srt_path = os.path.join(transcripts_folder, output_srt_filename)

    # Generate the transcript using Whisper
    with open(audio_file_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="srt"
        )
        
    # Write the response to an SRT file
    with open(output_srt_path, "w") as srt_file:
        srt_file.write(response)
    
    return output_srt_path

# Function to parse the SRT file
def parse_srt(srt_file):
    with open(srt_file, 'r') as file:
        content = file.read()

    subtitle_pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+?)(?=\n\n|\Z)', re.DOTALL)
    subtitles = []

    for match in subtitle_pattern.finditer(content):
        start_time_str = match.group(2)
        end_time_str = match.group(3)
        text = match.group(4).replace('\n', ' ')

        # Convert timestamp to seconds
        start_time = timestamp_to_seconds(start_time_str)
        end_time = timestamp_to_seconds(end_time_str)

        subtitles.append((start_time, end_time, text))

    return subtitles

# Function to convert timestamp to seconds
def timestamp_to_seconds(timestamp):
    hours, minutes, seconds = timestamp.split(':')
    seconds, milliseconds = seconds.split(',')
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000

# Function to add subtitles to video
def add_subtitles_to_video(video_file, audio_file, output_video_with_subs, output_folder="final_videos"):
    # Generate the SRT file using Whisper
    srt_file = generate_srt_from_audio(audio_file)

    # Load the video
    video = VideoFileClip(video_file)

    # Parse the SRT file to get subtitle timings and text
    subtitles = parse_srt(srt_file)

    # Create TextClips for each subtitle line
    text_clips = []

    for start_time, end_time, text in subtitles:
        duration = end_time - start_time
        # Create a TextClip for each subtitle phrase
        text_clip = TextClip(
            text,
            fontsize=24,
            color='white',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=2
        ).set_position(('center', 'bottom')).set_start(start_time).set_duration(duration)

        text_clips.append(text_clip)

    # Overlay subtitles on the video
    video_with_subtitles = CompositeVideoClip([video] + text_clips)

    # Ensure the output folder exists for the final video
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_path = os.path.join(output_folder, output_video_with_subs)

    # Write the final video with subtitles
    video_with_subtitles.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)

    return output_path
