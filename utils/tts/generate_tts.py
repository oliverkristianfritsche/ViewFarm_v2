import os
import json
from pathlib import Path
from pydub import AudioSegment
import torch
from TTS.api import TTS
from deep_translator import GoogleTranslator
from datetime import datetime, timedelta

# Constants
AUDIO_DIR = Path('/root/tmp/audio_files')
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
tts_frog = None

def save_wav(wav, file_path):
    if isinstance(wav, list):
        wav = torch.tensor(wav)
    
    wav = torch.clamp(wav, min=-1, max=1)
    wav = (wav * 32767).squeeze().cpu().numpy().astype('int16')
    audio_segment = AudioSegment(data=wav.tobytes(), sample_width=2, frame_rate=22050, channels=1)
    audio_segment.export(file_path, format="wav")

def generate_audio_tts_frog(text, filename, speaker_wav="/root/speaker.wav", lang='en'):
    global tts_frog
    try:

        if tts_frog is None:
            # Initialize 🐸TTS
            device = "cuda" if torch.cuda.is_available() else "cpu"
            tts_frog = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

        print(f"Generating 🐸TTS audio: {filename} in {lang}")
        file_path = AUDIO_DIR / filename

        if file_path.exists():
            print(f"Audio file {filename} already exists in the output directory. Skipping.")
            return file_path, speaker_wav
        wav_output = tts_frog.tts(text=text, speaker_wav=speaker_wav, language=lang)
        save_wav(wav_output, file_path)
        return file_path, speaker_wav
    except Exception as e:
        print(f"Failed to generate 🐸TTS audio for {filename} in {lang}: {e}")
        return None, None

def get_audio_length(file_path):
    try:
        audio = AudioSegment.from_file(file_path)
        length = len(audio) / 1000
        print(f"Audio length for {file_path}: {length} seconds")
        return length
    except Exception as e:
        print(f"Failed to get audio length for {file_path}: {e}")
        return 0

TTS_ENGINES = {
    'frog_tts': generate_audio_tts_frog
}

def tts_generate_and_save(story_id, text, method, language, speaker_wav="/root/speaker_americanpyscho.wav"):
    filename = f"{story_id}_combined_{method}_{language}_{speaker_wav[6:]}"
    file_path = AUDIO_DIR / filename

    # Check if the audio file already exists in the output directory
    if file_path.exists():
        print(f"Audio file {filename} already exists in the output directory. Adding to the database.")
        # Check if the file is already in the database
        existing_audio_file = get_audio_file_path(story_id, method, language, speaker_wav)
        if not existing_audio_file:
            length = get_audio_length(file_path)
            save_audio_file(story_id, str(file_path), length, method, language, speaker_wav)
            print(f"Audio file {filename} added to the database with length {length} seconds.")
        else:
            print(f"Audio file {filename} already exists in the database. Skipping.")
        return

    # If the audio file does not exist, generate it
    existing_audio_file = get_audio_file_path(story_id, method, language, speaker_wav)
    if existing_audio_file:
        print(f"TTS audio for story {story_id} in {language} with method {method} already exists in the database. Skipping.")
        return

    tts_func = TTS_ENGINES.get(method)
    if not tts_func:
        print(f"TTS method {method} is not supported.")
        return

    audio_file_path, speaker_file = tts_func(text, filename, speaker_wav=speaker_wav, lang=language)

    global tts_frog

    if tts_frog is None:
        # Initialize 🐸TTS
        device = "cuda" if torch.cuda.is_available() else "cpu"
        tts_frog = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    
    if audio_file_path and audio_file_path.exists():
        length = get_audio_length(audio_file_path)
        save_audio_file(story_id, str(audio_file_path), length, method, language, speaker_file)
        print(f"Audio file {filename} generated and saved with length {length} seconds.")
    else:
        print(f"Audio generation failed for {filename}.")

def translate_text_if_needed(text, target_language, input_lang="en"):
    try:
        translated_text = GoogleTranslator(source=input_lang, target=target_language).translate(text)
        return translated_text
    except Exception as e:
        print(f"Failed to translate text: {e}. Using original text.")
        return text

def load_config(config_file='config.json'):
    with open(config_file, 'r') as file:
        return json.load(file)