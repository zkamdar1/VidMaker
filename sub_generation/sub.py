import os
import re
import time
import chardet
from google.cloud import speech_v1p1beta1 as speech
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

timestamp = int(time.time())

def generate_word_level_srt(audio_file_path, transcripts_folder="transcripts", output_srt_filename=f"transcript{timestamp}.srt", max_words_per_chunk=3):
    # Ensure the output folder for transcripts exists
    if not os.path.exists(transcripts_folder):
        os.makedirs(transcripts_folder)

    # Generate full path for the output SRT file
    output_srt_path = os.path.join(transcripts_folder, output_srt_filename)

    # Initialize the Google Cloud client
    client = speech.SpeechClient()

    # Load the audio file
    with open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,  # Adjust as needed
        sample_rate_hertz=16000,  # Adjust as needed
        language_code="en-US",
        enable_word_time_offsets=True,
    )

    # Perform the transcription using long_running_recognize
    try:
        operation = client.long_running_recognize(config=config, audio=audio)
        print('Waiting for operation to complete...')
        response = operation.result(timeout=300)
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return None

    if not response.results:
        print("No transcription results were returned.")
        return None

    # Process the response to create SRT
    srt_lines = []
    counter = 1
    words = []

    # Accumulate words and group them
    for result in response.results:
        alternative = result.alternatives[0]
        print(f"Transcript chunk: {alternative.transcript}")

        for word_info in alternative.words:
            word = word_info.word
            words.append({
                "word": word,
                "start_time": word_info.start_time,
                "end_time": word_info.end_time,
            })

            # If we've reached the max words per chunk, or it's the last word, create a subtitle
            if len(words) >= max_words_per_chunk:
                srt_lines.append(create_srt_chunk(words, counter))
                counter += 1
                words = []  # Reset for the next chunk

    # If any words are left unprocessed, add them
    if words:
        srt_lines.append(create_srt_chunk(words, counter))

    # Write SRT to file
    with open(output_srt_path, "w", encoding='utf-8') as srt_file:
        srt_file.writelines(srt_lines)

    print(f"SRT file generated at {output_srt_path}")
    return output_srt_path


# Helper function to create SRT chunk
def create_srt_chunk(words, counter):
    start_time_srt = format_timestamp(words[0]["start_time"])
    end_time_srt = format_timestamp(words[-1]["end_time"])
    text = " ".join([word_info["word"] for word_info in words])

    return f"{counter}\n{start_time_srt} --> {end_time_srt}\n{text}\n\n"

# Helper function to format timestamp for SRT
def format_timestamp(timestamp):
    total_seconds = timestamp.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds % 1) * 1000)

    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


# Function to add subtitles to video
def add_subtitles_to_video(video_file, srt_file, output_video_with_subs, output_folder="final_videos"):
    # Load the video
    video = VideoFileClip(video_file)

    # Parse the SRT file to get subtitle timings and text
    subtitles = parse_srt(srt_file)

    # Create TextClips for each subtitle line
    text_clips = []

    for start_time, end_time, text in subtitles:
        duration = end_time - start_time

        # Create a TextClip for each subtitle phrase with requested styles
        text_clip = TextClip(
            text,
            fontsize=80,  # Bold and larger font for emphasis
            color='white',
            font='Arial-Bold',  # Custom bold font, ensure it's available
            stroke_color='black',  # Outline for readability
            stroke_width=2  # Slightly increased stroke width for emphasis
        ).set_position(('center', 'center')).set_start(start_time).set_duration(duration)

        # Append text clip
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

# Function to parse the SRT file
def parse_srt(srt_file):
    # Detect file encoding
    with open(srt_file, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
    
    # Open the file with detected encoding
    with open(srt_file, 'r', encoding=encoding) as file:
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
