from openai import OpenAI
import os
client = OpenAI()

# Set your OpenAI API key
client.api_key = os.getenv("OPENAI_API_KEY")

def generate_audio(script_text):
    # Extract the first word from script_text
    first_word = script_text.split()[0].lower()  # Use `.lower()` to ensure filename is case insensitive

    # Generate the output audio file name using the first word
    output_audio_file = f"output_audio_{first_word}.mp3"

    response = client.audio.speech.create(
        model="tts-1",
        input=script_text,
        voice="onyx",
    )

    with open(output_audio_file, 'wb') as audio_file:
        audio_file.write(response.content)

    return output_audio_file


# Example usage
#if __name__ == "__main__":
#    script = "AI can help solve complex healthcare problems by analyzing medical data."
#    generate_audio(script)
