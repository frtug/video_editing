import os
import numpy as np
from PIL import Image
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, AudioFileClip
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range

def join_videos(folder_path):
    # Get all video files in the folder and sort them numerically
    video_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.mov')], 
                         key=lambda x: int(os.path.splitext(x)[0]))
    
    # Load all video clips
    clips = [VideoFileClip(os.path.join(folder_path, video)) for video in video_files]
    
    # Concatenate all clips
    final_clip = concatenate_videoclips(clips)
    
    return final_clip

def process_audio(audio_path, output_path):
    # Load the audio
    audio = AudioSegment.from_file(audio_path)
    
    # Normalize the audio
    audio = normalize(audio)
    
    # Apply noise reduction (this is a basic approach, might need tuning)
    audio = audio.low_pass_filter(3000)
    audio = audio.high_pass_filter(300)
    
    # Compress the dynamic range to enhance voice
    audio = compress_dynamic_range(audio)
    
    # Export the processed audio
    audio.export(output_path, format="wav")

def overlay_face_video(base_video, face_video_path):
    # Load the face video
    face_clip = VideoFileClip(face_video_path)
    
    # Process the audio
    temp_audio_path = "temp_processed_audio.wav"
    process_audio(face_video_path, temp_audio_path)
    
    # Load the processed audio
    processed_audio = AudioFileClip(temp_audio_path)
    
    # Replace the original audio with the processed audio
    face_clip = face_clip.set_audio(processed_audio)
    
    # Define a function to resize frames using the updated Pillow method
    def resize_frame(image):
        pil_image = Image.fromarray(image)
        resized_pil = pil_image.resize((int(face_clip.w * 200 / face_clip.h), 200), Image.LANCZOS)
        return np.array(resized_pil)

    # Resize the face video to a smaller size (adjust as needed)
    face_clip_resized = face_clip.fl_image(resize_frame)
    
    # Position the face video in the top-right corner
    face_clip_positioned = face_clip_resized.set_position(("right", "bottom"))
    
    # Create the final composite
    final_video = CompositeVideoClip([base_video, face_clip_positioned])
    
    # Clean up temporary file
    os.remove(temp_audio_path)
    
    return final_video

# ... (rest of the script remains the same)
def main():
    # Folder containing numbered videos
    folder_path = "screen_recording"
    
    # Path to your face video
    face_video_path = "face.mov"
    
    # Output video path
    output_path = "final_video.mp4"
    
    print("Joining videos...")
    joined_video = join_videos(folder_path)
    
    print("Overlaying face video...")
    final_video = overlay_face_video(joined_video, face_video_path)
    
    print("Writing final video...")
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
    print("Video processing completed!")

if __name__ == "__main__":
    main()