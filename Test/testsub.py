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
        language_code="en-US",
        sample_rate_hertz=16000,
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

    # Removed print statement
    return response

if __name__ == "__main__":
    audio_file_path = "output_audio_1731013044.mp3"  # Replace with your actual audio file path
    transcripts_folder = "transcripts"  # Folder where SRT file will be saved
    output_srt_filename = f"transcript{timestamp}.srt"  # Desired output SRT filename

    srt_file_path = generate_word_level_srt(audio_file_path, transcripts_folder, output_srt_filename)

    if srt_file_path:
        print(f"SRT file created at: {srt_file_path}")
    else:
        print("Failed to generate SRT.")