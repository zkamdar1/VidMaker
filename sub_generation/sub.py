import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

def add_subtitles_to_video(video_file, subtitle_text, output_video_with_subs="final_with_subtitles.mp4", output_folder="final_videos"):
    video = VideoFileClip(video_file)

    # Create a TextClip for each line of subtitles and set its position
    text_clip = TextClip(subtitle_text, fontsize=24, color='white', font='Arial-Bold', stroke_color='gray', stroke_width=1.3)
    text_clip = text_clip.set_position(('center', 'center')).set_duration(video.duration)

    # Overlay subtitles on the video
    video_with_subtitles = CompositeVideoClip([video, text_clip])

     # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    output_path = os.path.join(output_folder, output_video_with_subs)

    # Write the final video with subtitles
    video_with_subtitles.write_videofile(output_path, codec="libx264", audio_codec="aac")
    return output_path
