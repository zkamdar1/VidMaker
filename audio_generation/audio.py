from gtts import gTTS

def generate_audio(script_text, output_audio_file="output_audio.mp3"):
    tts = gTTS(text=script_text, lang='en')
    tts.save(output_audio_file)
    return output_audio_file
