import os
import json
import torch
import whisper
from TTS.api import TTS
from moviepy.editor import VideoFileClip, AudioFileClip
from deep_translator import GoogleTranslator
from pydub import AudioSegment
import numpy as np

device = "cuda:0" if torch.cuda.is_available() else "cpu"

# Load the configuration from config.json
with open('config.json', 'r') as f:
    config = json.load(f)

# Get configurations from the config file
target_language = config.get('target_language', 'es')
whisper_model_size = config.get('whisper_model_size', 'small')
temp_audio_path = config.get('temp_audio_path', '/root/tmp/temp_audio.wav')
tts_model = config.get('tts_model', 'tts_models/multilingual/multi-dataset/xtts_v2')
speaker_file = config.get('speaker_file', '/root/speakers/speaker_americanpyscho.wav')
audio_output_path = config.get('audio_output_path', '/root/tmp/output.wav')
intro_text = config.get('intro_text', 'Hello, welcome!')
outro_text = config.get('outro_text', 'zài jiàn!')
adjusted_audio_path = config.get('adjusted_audio_path', '/root/tmp/adjusted_output.wav')
final_video_path = config.get('final_video_path', '/root/tmp/final_video.mp4')

tts_frog = None
def generate_audio_tts_frog(text, lang='en'):
    global tts_frog
    try:
        if tts_frog is None:
            tts_frog = TTS(tts_model).to(device)
        print(f"Generating 🐸TTS audio: {speaker_file} in {target_language}")
        wav_output = tts_frog.tts(text=text, speaker_wav=speaker_file, language=target_language)
        save_wav(wav_output, audio_output_path)
        return wav_output
    except Exception as e:
        print(f"Failed to generate 🐸TTS audio for {speaker_file} in {target_language}: {e}")
        return None

def save_wav(wav, file_path):
    if isinstance(wav, list):
        wav = np.array(wav)
    
    wav = np.clip(wav, -1, 1)
    wav = (wav * 32767).astype(np.int16)
    audio_segment = AudioSegment(data=wav.tobytes(), sample_width=2, frame_rate=22050, channels=1)
    audio_segment.export(file_path, format="wav")

def adjust_audio_speed(audio_path, target_duration, output_path):
    audio = AudioSegment.from_file(audio_path)
    current_duration = len(audio) / 1000.0  # Convert to seconds
    speed_ratio = current_duration / target_duration
    
    # Adjust the speed
    new_audio = audio._spawn(audio.raw_data, overrides={
        "frame_rate": int(audio.frame_rate * speed_ratio)
    }).set_frame_rate(audio.frame_rate)
    
    # Export the adjusted audio
    new_audio.export(output_path, format="wav")
    return output_path

def replace_audio_in_video(video_path, audio_path, output_video_path):
    video = VideoFileClip(video_path)
    new_audio = AudioFileClip(audio_path)
    
    # Set the new audio to the video
    video = video.set_audio(new_audio)
    
    # Write the result to the output video
    video.write_videofile(output_video_path, codec='libx264', audio_codec='aac')

# Load Whisper model
whisper_model = whisper.load_model(whisper_model_size)

# Find the only .mp4 file in the /root/tmp directory
mp4_files = [f for f in os.listdir('/root/tmp') if f.endswith('.mp4')]
if len(mp4_files) != 1:
    raise FileNotFoundError("There should be exactly one .mp4 file in the /root/tmp directory.")

mp4_path = os.path.join('/root/tmp', mp4_files[0])

# Extract audio from the video file
video = VideoFileClip(mp4_path)
video.audio.write_audiofile(temp_audio_path)

# Run Whisper on the extracted audio
result = whisper_model.transcribe(temp_audio_path)

# Print the original transcription
original_text = result['text']
print("Original transcription:", original_text)

# Initialize the GoogleTranslator
translator = GoogleTranslator(source='auto', target=target_language)

# Translate the transcription to the target language
translated_text = translator.translate(original_text)
print("Translated text:", translated_text)

translated_text = f"{intro_text} {translated_text} {outro_text}"

# Generate TTS audio
new_wav = generate_audio_tts_frog(translated_text, lang=target_language)

# Get the original video length
video_length = video.duration

# Adjust the TTS-generated audio to match the video length
adjust_audio_speed(audio_output_path, video_length, adjusted_audio_path)

# Replace the original audio in the video with the new, adjusted audio
replace_audio_in_video(mp4_path, adjusted_audio_path, final_video_path)

print(f"Final video saved to: {final_video_path}")
