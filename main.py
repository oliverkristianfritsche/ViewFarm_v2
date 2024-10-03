import json
import os
import shutil
import random
import logging
import contextlib
import sys
from tqdm import tqdm
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, concatenate_audioclips
from moviepy.video.fx.all import speedx as video_speedx
from moviepy.video.fx.all import speedx  # General speedx function that can be used for both video and audio
from pathlib import Path
from scrappers.shorts_scrapper import scrape_shorts
from scrappers.reddit_scrapper import init_reddit_client, get_top_n_hot_threads, get_post_details
from downloaders.youtube_downloader import download_video
from tts.generate_tts import generate_audio_tts_frog, translate_text_if_needed
from dask.distributed import Client, wait

# Load JSON config
config = json.load(open('config.json'))

def adjust_audio_speed(audio_file, speed):
    audio_file = str(audio_file)
    audio = AudioFileClip(audio_file).fx(speedx, speed)
    return audio

def adjust_video_speed(video_path, speed):
    video_path = str(video_path)
    video = VideoFileClip(video_path)
    return video.fx(video_speedx, speed)

def generate_tts_with_fallback(text, filename, language):
    try:
        with contextlib.redirect_stdout(sys.stderr):
            tts_file_path, _ = generate_audio_tts_frog(text, filename, config["speaker_file"], language)
        return tts_file_path
    except Exception as e:
        logging.error(f"Failed to generate TTS audio: {e}")
        return None

def split_text_into_chunks(text, max_tokens=200):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(' '.join(current_chunk)) > max_tokens:
            chunks.append(' '.join(current_chunk[:-1]))
            current_chunk = [word]

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def truncate_filename(text, max_length=20):
    """
    Truncate the text to fit within the maximum filename length.
    If truncation occurs, ellipses are added to the end.
    """
    if len(text) > max_length:
        return text[:max_length-3] + '...'  # Truncate and append ellipses
    return text

def process_language(language, posts, downloaded_videos):
    language_dir = f'/root/reprocessio/{language}'
    os.makedirs(language_dir, exist_ok=True)

    for post in tqdm(posts, desc=f"Processing posts for {language}"):
        os.makedirs('/root/tmp/audio_files', exist_ok=True)
        post_id = post['id']
    
        post_details = get_post_details(reddit, post_id)
        post_text = post_details['title'] + '.' + post_details['body']
        
        translated_text = translate_text_if_needed(post_text, language)
        
        text_chunks = split_text_into_chunks(translated_text, max_tokens=200)
        audio_clips = []
        
        for i, chunk in enumerate(tqdm(text_chunks, desc="Generating TTS")):
            if chunk.strip():
                tts_filename = f"{post_id}_{language}_{i}.mp3"
                tts_file_path = generate_tts_with_fallback(chunk, tts_filename, language)
                
                if tts_file_path:
                    audio_clip = AudioFileClip(str(tts_file_path))
                    audio_clips.append(audio_clip)

        if not audio_clips:
            logging.error(f"No audio clips generated for post {post_id}. Skipping.")
            continue
        
        final_audio = concatenate_audioclips(audio_clips)
        shutil.rmtree('/root/tmp/audio_files')

        selected_videos = []
        total_video_duration = 0

        downloaded_videos_copy = downloaded_videos.copy()
        while total_video_duration < final_audio.duration:
            if not downloaded_videos_copy:
                logging.error(f"Ran out of video clips to use before meeting the audio duration for post {post_id}.")
                break

            video_file = random.choice(downloaded_videos_copy)
            downloaded_videos_copy.remove(video_file)

            try:
                video = adjust_video_speed(video_file, config["video_speed"])
            except Exception as e:
                logging.error(f"Error adjusting video speed for {video_file}: {e}")
                continue
            
            if video.duration > config["max_video_length"]:
                logging.info(f"Skipping video {video_file} as it exceeds max video length.")
                continue

            total_video_duration += video.duration
            selected_videos.append(video)
        
        if not selected_videos:
            logging.error(f"No valid video clips found for post {post_id}. Skipping.")
            continue

        final_video = concatenate_videoclips(selected_videos, method="compose").set_audio(None)
        final_video = final_video.set_audio(final_audio).subclip(0, final_audio.duration)

        # Truncate the filename to avoid issues with long file names
        safe_title = truncate_filename(translate_text_if_needed(post_details['title'], language), max_length=30)
        final_output_path = os.path.join(language_dir, f"{safe_title}.mp4")
        
        try:
            final_video.write_videofile(final_output_path, codec="libx264")
            print(f"Saved final video to {final_output_path}")
        except Exception as e:
            logging.error(f"Failed to write video for post {post_id} to {final_output_path}: {e}")

def process_language_dask(language, posts, downloaded_videos):
    process_language(language, posts, downloaded_videos)
    return f"Processed {language}"

if __name__ == "__main__":
    # Connect to Dask Scheduler (replace with the actual scheduler address)
    client = Client("tcp://192.168.3.132:8786")  # Replace <host-ip> with the actual IP of your host scheduler

    with contextlib.redirect_stdout(sys.stderr):  # Redirect stdout to suppress unwanted prints
        trending_shorts = scrape_shorts()

    for video in tqdm(trending_shorts, desc="Downloading videos"):
        video_id = video['id'] if config['youtubescrapper']['searchBy'] == 'trending' else video['id']['videoId']
        download_video(video_id)

    # Get paths of all mp4 files in /root/tmp/raw_shorts
    downloaded_videos = [os.path.join('/root/tmp/raw_shorts', file) for file in os.listdir('/root/tmp/raw_shorts') if file.endswith('.mp4')]

    reddit = init_reddit_client()
    posts = get_top_n_hot_threads(reddit, config['subreddits'], config['num_posts'])

    # Use Dask to distribute the processing of languages
    futures = [client.submit(process_language_dask, language, posts, downloaded_videos) for language in config['target_language']]

    # Wait for all tasks to complete
    wait(futures)

    # Close the Dask client
    client.close()

    print("All languages processed.")
