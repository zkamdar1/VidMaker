# Automatic Video Generator Project

This project generates videos from a given topic automatically.

## Information
- **Script Generation**: Uses OpenAI's GPT to generate a script.
- **Audio Generation**: Converts the script to audio using Google Text-to-Speech (gTTS).
- **Video Editing**: Combines video clips with the generated audio.
- **Subtitles**: Adds subtitles to the video.

## How to Use
1. Set your OpenAI API key in the `gpt_script.py` file.
2. Prepare video clips in a folder named `background_clips`.
3. Run the main application:
   ```sh
   python app.py
   ```