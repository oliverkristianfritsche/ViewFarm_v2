import os
from googleapiclient.discovery import build
from isodate import parse_duration
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from databases.ScrapedVideos_mongo import insert_scraped_video, get_video_by_id
from utils import load_json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv('YOUTUBE_API_KEY')

# Load configuration from config.json
config = load_json()

# Set up the YouTube API client
youtube = build("youtube", "v3", developerKey=api_key)

def video_exists(video_id):
    """
    Check if a video ID already exists in the database.
    :param video_id: The video ID to check.
    :return: True if the video exists, False otherwise.
    """
    # Modify the get_video_by_id function to query by the video_id field, not _id
    return get_video_by_id(video_id) is not None

def insert_scraped_shorts():
    """
    Insert a single unique scraped short into the database.
    :return: ID of the inserted video.
    """
    scraped_videos = scrape_shorts()
    
    for video in scraped_videos:

        if config['youtubescrapper']['searchBy'] == 'trending':
            video_id = video['id']
        else:
            video_id = video['id']['videoId']

        # Check if the video already exists in the database using video_exists function
        if video_exists(video_id):
            print(f"Video ID {video_id} already exists in the database. Skipping.")
            continue
        
        # If it doesn't exist, proceed to insert
        link = f"https://www.youtube.com/watch?v={video_id}"
        author = video['snippet']['channelTitle']
        source = "YouTube"
        title = video['snippet']['title']
        description = video['snippet']['description']
        hashtags = []  # Assuming hashtags might be extracted separately, you can modify this logic
        num_comments = video['details'].get('comments', 0)
        num_likes = video['details'].get('likes', 0)
        num_views = video['details'].get('views', 0)
        length = video['details'].get('duration', 0)
        botid = config['botid']
        dateposted = video['snippet']['publishedAt']
        thumbnails = video['snippet']['thumbnails']

        try:
            inserted_id = insert_scraped_video(
                video_id, link, author, source, title, description, hashtags, num_comments, num_likes, num_views, length, botid, dateposted, thumbnails
            )
            if inserted_id:
                print(f"Inserted video ID: {inserted_id}")
                return inserted_id  # Return immediately after successfully inserting a unique video
        except Exception as e:
            print(f"Error inserting video {video_id}: {e}")
            continue  # Move to the next video in case of an error (e.g., duplicate key)

    return None

def get_video_details(video_ids):
    """
    Fetch detailed information for a list of video IDs.
    :param video_ids: List of video IDs.
    :return: Dictionary containing video details (views, likes, comments, length).
    """
    request = youtube.videos().list(
        part="contentDetails,statistics",
        id=",".join(video_ids)
    )
    response = request.execute()

    video_details = {}
    for item in response.get('items', []):
        video_id = item['id']
        view_count = int(item['statistics'].get('viewCount', 0))
        like_count = int(item['statistics'].get('likeCount', 0))
        comment_count = int(item['statistics'].get('commentCount', 0))
        duration = parse_duration(item['contentDetails']['duration']).total_seconds()
        
        video_details[video_id] = {
            "views": view_count,
            "likes": like_count,
            "comments": comment_count,
            "duration": duration
        }

    return video_details

def scrape_shorts_by_account(account_id, max_results=None):
    """
    Scrape shorts from a specific YouTube account.
    :param account_id: YouTube channel ID of the account.
    :param max_results: Maximum number of results to fetch.
    :return: List of scraped video information.
    """
    max_results = max_results or config['youtube']['max_results']
    request = youtube.search().list(
        part="snippet",
        channelId=account_id,
        maxResults=max_results,
        type="video",
        videoDuration="short",
        videoType="any",
        order=config['youtube']['order']
    )
    response = request.execute()
    
    video_ids = [item['id']['videoId'] for item in response.get('items', [])]
    video_details = get_video_details(video_ids)

    for item in response.get('items', []):
        video_id = item['id']['videoId']
        item['details'] = video_details.get(video_id, {})

    return response.get('items', [])

def scrape_shorts_by_hashtag(hashtag, max_results=None):
    """
    Scrape shorts by a specific hashtag.
    :param hashtag: Hashtag to search for.
    :param max_results: Maximum number of results to fetch.
    :return: List of scraped video information.
    """
    max_results = max_results or config['youtubescrapper']['max_results']
    request = youtube.search().list(
        part="snippet",
        q=f"#{hashtag}",
        maxResults=max_results,
        type="video",
        videoDuration="short",
        videoType="any",
        order=config['youtubescrapper']['order']
    )
    response = request.execute()
    
    video_ids = [item['id']['videoId'] for item in response.get('items', [])]
    video_details = get_video_details(video_ids)

    for item in response.get('items', []):
        video_id = item['id']['videoId']
        item['details'] = video_details.get(video_id, {})

    return response.get('items', [])

def scrape_trending_shorts(region_code=None, max_results=None):
    """
    Scrape trending shorts.
    :param region_code: The region to get trending videos for.
    :param max_results: Maximum number of results to fetch.
    :return: List of scraped video information.
    """
    region_code = region_code or config['youtubescrapper']['region_code']
    max_results = max_results or config['youtubescrapper']['max_results']
    request = youtube.videos().list(
        part="snippet",
        chart="mostPopular",
        regionCode=region_code,
        maxResults=max_results,
        videoCategoryId=config['youtubescrapper']['shorts_category_id']
    )
    response = request.execute()
    
    video_ids = [item['id'] for item in response.get('items', [])]
    video_details = get_video_details(video_ids)

    for item in response.get('items', []):
        video_id = item['id']
        item['details'] = video_details.get(video_id, {})

    return response.get('items', [])



def scrape_shorts():
    """
    Scrape shorts from multiple sources.
    :return: List of scraped video information.
    """
    method = config['youtubescrapper']['searchBy']
    searchValue = config['youtubescrapper']['searchValue']
    maxResults = config['youtubescrapper']['maxResults']

    if method == 'account':
        return scrape_shorts_by_account(searchValue, maxResults)
    elif method == 'hashtag':
        return scrape_shorts_by_hashtag(searchValue, maxResults)
    elif method == 'trending':
        return scrape_trending_shorts(searchValue, maxResults)
    
    else:
        assert False, "Invalid scrape method"


if __name__ == "__main__":
    print(insert_scraped_shorts())
