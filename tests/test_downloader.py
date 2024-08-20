import os
import sys
import yt_dlp

# Assuming the path to the `shorts_scrapper.py` script is in the parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scrappers.shorts_scrapper import insert_scraped_shorts

def download_video(video_id):
    """
    Download a YouTube video given its video ID using yt-dlp.
    :param video_id: The video ID to download.
    :return: None
    """

    try:
        # Construct the full YouTube URL
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{video_id}.mp4',  # Save the video with its ID as the filename
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        print(f"Video {video_id} downloaded successfully.")
    except Exception as e:
        print(f"Error downloading video {video_id}: {e}")

if __name__ == "__main__":
    # Insert the scraped shorts and get the video ID of the inserted video
    video_id = insert_scraped_shorts()

    # If a video was successfully inserted, download it
    if video_id:
        download_video(video_id)
    else:
        print("No new video to download.")
