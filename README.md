# Nebula - Automatic Video Generator Project

Welcome to **Nebula**, an automatic video generator project. Nebula takes a topic and turns it into a complete video with background visuals, corresponding audio narration, and subtitles. Below, you'll find a detailed overview of the project structure, how it works step-by-step, and how to use it.

## Project Overview
**Nebula** is a Python-based project that generates videos automatically. It comprises several steps:

1. **Script Generation**: Generates a script based on a topic using OpenAI's GPT model.
   - Files: `script_generation/script.py`

2. **Audio Generation**: Converts the generated script into an audio narration using Google Text-to-Speech.
   - Files: `audio_generation/audio.py`

3. **Video Editing**: Combines pre-existing background video clips with the generated audio to produce a cohesive video.
   - Files: `video_editing/video.py`, `background_clips/`

4. **Subtitle Generation**: Generates subtitles from the audio using Google's Speech API and adds them to the video.
   - Files: `sub_generation/sub.py`, `transcripts/`

5. **Music Integration**: Adds background music to the video.
   - Files: `music_generation/music.py`, `music_clips/`

6. **Final Output**: The finished video with audio, music, and subtitles is saved in the `final_videos/` folder.

## Folder and File Structure
Here is a detailed explanation of the Nebula project folder and file structure:

```
VIDEO_MAKER/
├── .venv/                         # Virtual environment folder for dependencies
├── audio_generation/              # Audio generation module
│   ├── audio.py                  # Generates audio from script text
│   └── __init__.py               # Initializes audio generation module
├── audio_outputs/                 # Contains generated audio files
├── audio_vids/                    # Contains videos with audio added
├── background_clips/              # Folder containing background video clips
│   ├── clips.py                  # Utility script for handling background clips
│   └── __init__.py               # Initializes background clips module
├── final_videos/                  # Folder for final output videos with subtitles
├── music_clips/                   # Folder containing music clips for background
├── music_generation/              # Music generation module
│   ├── music.py                  # Generates and selects background music for videos
│   └── __init__.py               # Initializes music generation module
├── script_generation/             # Script generation module
│   ├── script.py                 # Generates the script using OpenAI's GPT model
│   └── __init__.py               # Initializes script generation module
├── sub_generation/                # Subtitle generation module
│   ├── sub.py                    # Generates and adds subtitles to the video
│   └── __init__.py               # Initializes subtitle generation module
├── sub_vids/                      # Contains videos with subtitles added
├── Test/                          # Testing module for individual components
│   ├── test.py                   # Test scripts
│   └── __init__.py               # Initializes testing module
├── transcripts/                   # Folder containing generated transcript files
│   ├── transcript.py             # Handles transcript generation
│   └── __init__.py               # Initializes transcripts module
├── utils/                         # Utility functions and helpers
│   ├── utils.py                  # Contains utility functions like ensuring folder exists
│   └── __init__.py               # Initializes utils module
├── video_editing/                 # Video editing module
│   ├── video.py                  # Adds audio to video and handles video concatenation
│   └── __init__.py               # Initializes video editing module
├── __init__.py                    # Initializes the main package
├── app.py                         # Main entry point for generating videos
└── README.md                      # Project documentation
```

## Step-by-Step Process
This section explains the process of generating a video using Nebula, along with the associated files.

### 1. Script Generation
**File**: `script_generation/script.py`

- The first step is to generate a script based on a user-provided topic. Nebula uses OpenAI's GPT model to create a script that serves as the narration for the video.
- The script text is generated when you run the `app.py` script, which calls the `generate_script()` function from `script_generation/script.py`.

### 2. Audio Generation
**File**: `audio_generation/audio.py`

- Once the script is generated, Nebula converts it into an audio file using Google Text-to-Speech.
- The `generate_audio()` function in `audio_generation/audio.py` takes the script text and generates an audio file, which is saved in the `audio_outputs/` folder.

### 3. Video Editing
**Files**: `video_editing/video.py`, `background_clips/`

- In this step, Nebula takes the background clips stored in the `background_clips/` folder and combines them with the generated audio.
- The `add_audio_to_video()` function from `video_editing/video.py` handles video concatenation, trims clips to match the length of the audio, and adds the audio to the video.
- The output video with audio is stored in the `audio_vids/` folder.

### 4. Subtitle Generation
**Files**: `sub_generation/sub.py`, `transcripts/`

- Nebula uses Google's Speech API to transcribe the audio and generate word-level subtitle timings. The subtitles are saved as SRT files in the `transcripts/` folder.
- The `generate_word_level_srt()` function in `sub_generation/sub.py` creates the SRT file, while `add_subtitles_to_video()` adds the subtitles to the final video.
- The output video with subtitles is saved in the `sub_vids/` folder.

### 5. Music Integration
**Files**: `music_generation/music.py`, `music_clips/`

- Nebula adds background music to enhance the overall video experience. Music clips are stored in the `music_clips/` folder.
- The `add_music_to_video()` function in `music_generation/music.py` handles adding background music to the video.

### 6. Final Output
**Folder**: `final_videos/`

- The final video, complete with background visuals, audio narration, music, and subtitles, is saved in the `final_videos/` folder.

## How to Use Nebula
### Prerequisites
- Python 3.7 or higher
- API keys for OpenAI and Google Cloud Speech-to-Text
- Dependencies listed in `requirements.txt`

### Installation
1. Clone the repository to your local machine:
   ```sh
   git clone https://github.com/yourusername/nebula.git
   ```
2. Navigate to the project directory:
   ```sh
   cd nebula
   ```
3. Create a virtual environment and activate it:
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```
4. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Running Nebula
1. Set your OpenAI and Google Cloud API keys:
   ```sh
   export OPENAI_API_KEY="your_openai_api_key"
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/google_credentials.json"
   ```
2. Run the main application:
   ```sh
   python app.py
   ```
3. Follow the prompts to generate a video. The final video will be saved in the `final_videos/` folder.

## Future Improvements
- **Web Interface**: Implement a web-based interface for ease of use.
- **User Management**: Add user authentication and allow users to save and view their generated videos.
- **Advanced Editing**: Incorporate more sophisticated video effects and transitions.


## Contact
For any questions or suggestions, please contact [Your Name](mailto:your.email@example.com).

---
Thanks for checking out Nebula! We hope you enjoy using this automatic video generator.

