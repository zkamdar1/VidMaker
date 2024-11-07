from openai import OpenAI
import time
import os
from moviepy.editor import AudioFileClip, concatenate_audioclips

client = OpenAI()

# Set your OpenAI API key
client.api_key = os.getenv("OPENAI_API_KEY")

def generate_audio(script_text, output_folder="audio_outputs"):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    timestamp = int(time.time())

    # Generate the output audio file name using the first word, saved in the specified folder
    output_audio_file = os.path.join(output_folder, f"output_audio_{timestamp}.mp3")

    # Call the API to create the audio content
    response = client.audio.speech.create(
        model="tts-1",
        input=script_text,
        voice="onyx",
    )

    # Write the audio file to the specified folder
    with open(output_audio_file, 'wb') as audio_file:
        audio_file.write(response.content)

    # Add silence to the end of the audio
    original_audio = AudioFileClip(output_audio_file)
    silence_duration = 1.5  # 1.5 seconds of silence
    silent_audio = AudioFileClip(os.path.join("background_clips", "silence.mp3")).set_duration(silence_duration)

    # Concatenate original audio with silent audio
    final_audio = concatenate_audioclips([original_audio, silent_audio])

    # Write the final audio to a new file
    final_output_audio_file = os.path.join(output_folder, f"output_audio_final_{timestamp}.mp3")
    final_audio.write_audiofile(final_output_audio_file)

    return final_output_audio_file


# Example usage
#if __name__ == "__main__":
#    script = "AI can help solve complex healthcare problems by analyzing medical data."
#    generate_audio(script)
