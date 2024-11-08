# Import necessary modules
import os
import re
import time
import chardet
import shutil
from google.cloud import speech_v1p1beta1 as speech
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

timestamp = int(time.time())

def generate_word_level_srt(
    audio_file_path,
    transcripts_folder="transcripts",
    output_srt_filename=f"transcript{timestamp}.srt",
):
    # Ensure the output folder for transcripts exists
    os.makedirs(transcripts_folder, exist_ok=True)

    # Generate full path for the output SRT file
    output_srt_path = os.path.join(transcripts_folder, output_srt_filename)

    # Initialize the Google Cloud client
    client = speech.SpeechClient()

    # Load the audio file
    with open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)

    # Configure the recognition settings
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,  # Adjust if needed
        language_code="en-US",
        sample_rate_hertz=16000,
        enable_word_time_offsets=True,
    )

    # Perform the transcription using long_running_recognize
    try:
        operation = client.long_running_recognize(config=config, audio=audio)
        print("Waiting for operation to complete...")
        response = operation.result(timeout=600)
        print("Transcription completed.")
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return None

    if not response.results:
        print("No transcription results were returned.")
        return None

    # Process the response to create SRT entries for each word
    srt_lines = []
    counter = 1

    for result in response.results:
        alternative = result.alternatives[0]
        words = alternative.words

        for word in words:
            # Extract start and end times using total_seconds()
            start_time_seconds = word.start_time.total_seconds()
            end_time_seconds = word.end_time.total_seconds()
            word_text = word.word.strip()

            # Ensure that end_time is after start_time
            if end_time_seconds <= start_time_seconds:
                end_time_seconds = start_time_seconds + 0.1  # Add a small duration

            # Format the timestamps into SRT format
            start_time_srt = format_timestamp(start_time_seconds)
            end_time_srt = format_timestamp(end_time_seconds)

            # Create SRT entry
            srt_lines.append(f"{counter}\n{start_time_srt} --> {end_time_srt}\n{word_text}\n\n")
            counter += 1

    # Write the SRT file
    with open(output_srt_path, "w", encoding="utf-8") as srt_file:
        srt_file.writelines(srt_lines)

    print(f"SRT file created at: {output_srt_path}")
    print(response)
    return output_srt_path



def format_timestamp(total_seconds):
    # Convert seconds to hours, minutes, seconds, milliseconds
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int(round((total_seconds % 1) * 1000))

    # Format into SRT timestamp format
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


# Function to add subtitles to video
def add_subtitles_to_video(video_file, srt_file, output_video_with_subs, output_folder="sub_vids"):
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


    for i, (start_time, end_time, text) in enumerate(subtitles):
        duration = end_time - start_time

        # Calculate desired vertical position (adjust the multiplier to move text higher or lower)
        text_y_position = int(video_height * 0.44)  # 40% from the top

        # Create shadow TextClip
        shadow_text_clip = TextClip(
            text.upper(),
            fontsize=55,
            color='black',  # Shadow color
            font='Palatino-Bold',  # Ensure this font is available or provide the path
            stroke_color='black',
            stroke_width=5,
            method='caption',
            size=(max_text_width, None),
            align='center',
            interline=-5
        ).set_position(('center', text_y_position)).set_start(start_time).set_duration(duration)


        # Create a TextClip for each subtitle phrase with requested styles
        text_clip = TextClip(
            text.upper(),  # Convert text to uppercase
            fontsize=55,   # Slightly smaller font size
            color='white',
            font='Palatino-Bold',  # Updated font
            stroke_color='white',  # Outline for readability
            stroke_width=2.5,        # Increased stroke width for more pronounced outline
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
    video_with_subtitles.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=video.fps)

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

if __name__ == "__main__":
    audio_file_path = "audio_outputs/output_audio_final_1731030370.mp3"  # Replace with your actual audio file path
    transcripts_folder = "transcripts"  # Folder where SRT file will be saved
    output_srt_filename = f"transcript{timestamp}.srt"  # Desired output SRT filename

    srt_file_path = generate_word_level_srt(audio_file_path, transcripts_folder, output_srt_filename)

    if srt_file_path:
        print(f"SRT file created at: {srt_file_path}")
    else:
        print("Failed to generate SRT.")
