from google.cloud import speech

client = speech.SpeechClient()

# Path to your audio file
audio_file_path = 'audio_outputs/output_audio_1731016706.mp3'

with open(audio_file_path, 'rb') as f:
    content = f.read()

audio = speech.RecognitionAudio(content=content)
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.MP3,  # Adjust as needed
    sample_rate_hertz=16000,  # Adjust as needed
    language_code='en-US',
)

response = client.recognize(config=config, audio=audio)

for result in response.results:
    print('Transcript:', result.alternatives[0].transcript)
