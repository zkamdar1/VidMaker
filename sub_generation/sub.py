# Import necessary modules
import os
import re
import time
import chardet
import shutil
from google.cloud import speech_v1p1beta1 as speech
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

timestamp = int(time.time())

def generate_word_level_srt(audio_file_path, transcripts_folder="transcripts", output_srt_filename=f"transcript{timestamp}.srt"):
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
        # Removed print statement
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

    # Parameters to control subtitle grouping
    max_duration_per_subtitle = 5.0  # maximum duration in seconds
    max_chars_per_subtitle = 39      # maximum characters per subtitle
    max_time_gap = 0.63               # maximum allowed gap between words in seconds

    current_subtitle = {
        "start_time": None,
        "end_time": None,
        "words": [],
        "chars": 0,
        "duration": 0.0,
        "last_word_end_time": None,
    }

    # Accumulate words and group them based on timing and length
    for result in response.results:
        alternative = result.alternatives[0]
        # Removed print statement

        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time.total_seconds()
            end_time = word_info.end_time.total_seconds()
            word_duration = end_time - start_time
            time_gap = 0 if current_subtitle["last_word_end_time"] is None else start_time - current_subtitle["last_word_end_time"]

            # Check if we need to start a new subtitle
            if (current_subtitle["chars"] + len(word) + 1 > max_chars_per_subtitle or
                current_subtitle["duration"] + word_duration > max_duration_per_subtitle or
                time_gap > max_time_gap):

                # If there are words collected, create a subtitle chunk
                if current_subtitle["words"]:
                    srt_lines.append(create_srt_chunk(current_subtitle["words"], counter))
                    counter += 1
                    current_subtitle = {
                        "start_time": None,
                        "end_time": None,
                        "words": [],
                        "chars": 0,
                        "duration": 0.0,
                        "last_word_end_time": None,
                    }

            # Add word to current subtitle
            if current_subtitle["start_time"] is None:
                current_subtitle["start_time"] = word_info.start_time

            current_subtitle["end_time"] = word_info.end_time
            current_subtitle["words"].append({
                "word": word,
                "start_time": word_info.start_time,
                "end_time": word_info.end_time,
            })
            current_subtitle["chars"] += len(word) + 1  # +1 for space
            current_subtitle["duration"] = (current_subtitle["end_time"].total_seconds() - current_subtitle["start_time"].total_seconds())
            current_subtitle["last_word_end_time"] = end_time

    # Add any remaining words as a subtitle
    if current_subtitle["words"]:
        srt_lines.append(create_srt_chunk(current_subtitle["words"], counter))

    # Write SRT to file
    with open(output_srt_path, "w", encoding='utf-8') as srt_file:
        srt_file.writelines(srt_lines)

    # Removed print statement
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
    video_width = video.w
    video_height = video.h

    # Parse the SRT file to get subtitle timings and text
    subtitles = parse_srt(srt_file)

    # Create TextClips for each subtitle line
    text_clips = []

    # Define maximum width for the subtitle text box (e.g., 80% of video width)
    max_text_width = int(video_width * 0.88)

    for start_time, end_time, text in subtitles:
        duration = end_time - start_time

        # Calculate desired vertical position (adjust the multiplier to move text higher or lower)
        text_y_position = int(video_height * 0.43)  # 40% from the top

        # Create shadow TextClip
        shadow_text_clip = TextClip(
            text.upper(),
            fontsize=67,
            color='black',  # Shadow color
            font='Vollkorn-md',  # Ensure this font is available or provide the path
            stroke_color='black',
            stroke_width=10,
            method='caption',
            size=(max_text_width, None),
            align='center',
            interline=-5
        ).set_position(('center', text_y_position)).set_start(start_time).set_duration(duration)


        # Create a TextClip for each subtitle phrase with requested styles
        text_clip = TextClip(
            text.upper(),  # Convert text to uppercase
            fontsize=67,   # Slightly smaller font size
            color='white',
            font='Vollkorn-md',  # Updated font
            stroke_color='white',  # Outline for readability
            stroke_width=4,        # Increased stroke width for more pronounced outline
            method='caption',      # Enable text wrapping
            size=(max_text_width, None),  # Set the width, height will be auto-calculated
            align='center',        # Center-align the text
            interline=-5          # Adjust line spacing if needed
        ).set_position(('center', text_y_position)).set_start(start_time).set_duration(duration)

         # Append both shadow and main text clips
        text_clips.extend([shadow_text_clip, text_clip])

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


def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Remove the file or link
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Remove the directory and its contents
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')