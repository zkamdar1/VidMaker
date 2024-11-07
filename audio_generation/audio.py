from openai import OpenAI
import time
import os
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

    return output_audio_file


# Example usage
#if __name__ == "__main__":
#    script = "AI can help solve complex healthcare problems by analyzing medical data."
#    generate_audio(script)
