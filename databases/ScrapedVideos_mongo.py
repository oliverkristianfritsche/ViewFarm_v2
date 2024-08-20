from pymongo import MongoClient, ASCENDING
from bson.objectid import ObjectId
from utils import load_json
from datetime import datetime
from pymongo.errors import DuplicateKeyError

config = load_json()
# Connect to MongoDB (replace with your MongoDB connection string)
client_name = config['botid']
connection_string = config['database']['connection_string']
database_name = config['database']['name']

# Connect to MongoDB
client = MongoClient(connection_string)
db = client[database_name]
collection = db['ScrapedVideos']

# Get existing indexes
existing_indexes = collection.index_information()

# Function to safely create an index if it doesn't exist
def create_index_if_not_exists(collection, field_name, index_name=None, unique=False):
    if index_name is None:
        index_name = f"{field_name}_1"  # Default MongoDB index naming convention
    if index_name not in existing_indexes:
        collection.create_index([(field_name, ASCENDING)], name=index_name, unique=unique)

# Create indexes if they don't exist
create_index_if_not_exists(collection, "video_id", unique=True)
create_index_if_not_exists(collection, "url")
create_index_if_not_exists(collection, "author")
create_index_if_not_exists(collection, "source")
create_index_if_not_exists(collection, "botid")
create_index_if_not_exists(collection, "dateposted")
create_index_if_not_exists(collection, "title")
create_index_if_not_exists(collection, "hashtags")
create_index_if_not_exists(collection, "num_views")
create_index_if_not_exists(collection, "num_comments")
create_index_if_not_exists(collection, "length")

def insert_scraped_video(video_id,link, author, source, title, description, hashtags, num_comments, num_likes, num_views, length, botid, dateposted, thumbnails):
    video = {
        "video_id": video_id,
        "url": link,
        "author": author,
        "source": source,
        "title": title,
        "description": description,
        "hashtags": hashtags,
        "num_comments": num_comments,
        "num_likes": num_likes,
        "num_views": num_views,
        "datecreated": datetime.now(),
        "length": length,
        "botid": botid,
        "dateposted": dateposted,
        "thumbnails": thumbnails
    }
    
    try:
        collection.insert_one(video).inserted_id
        return video_id
    except DuplicateKeyError:
        print(f"Duplicate key error for URL: {link}. Attempting to scrape another video.")
        return None  # Or handle as needed, e.g., retry with a different video


# Getters
def get_video_by_id(video_id):
    """
    Retrieve a video document from the collection using the video_id.
    :param video_id: The video ID (YouTube video ID).
    :return: The video document if found, else None.
    """
    return collection.find_one({"video_id": video_id})

def get_video_by_link(link):
    return collection.find_one({"link": link})

def get_videos_by_author(author):
    return list(collection.find({"author": author}))

def get_videos_by_source(source):
    return list(collection.find({"source": source}))

def get_videos_by_botid(botid):
    return list(collection.find({"botid": botid}))

def get_videos_by_date(dateposted):
    return list(collection.find({"dateposted": dateposted}))

def get_videos_by_date_range(date_start, date_end):
    return list(collection.find({"dateposted": {"$gte": date_start, "$lte": date_end}}))

def get_videos_by_title(title):
    return list(collection.find({"title": title}))

def get_videos_by_hashtags(hashtags):
    return list(collection.find({"hashtags": {"$in": hashtags}}))


# Update category ID
def update_video_category_id_in_db(video_id, new_category_id):
    """
    Update the category ID of a video in the database.
    :param video_id: The ID of the video to update.
    :param new_category_id: The new category ID to set.
    :return: The result of the update operation.
    """
    result = collection.update_one(
        {"_id": ObjectId(video_id)},
        {"$set": {"category_id": new_category_id}}
    )
    return result.modified_count > 0


# Search by Multiple Parameters
def search_videos(params):
    query = {}
    if 'author' in params:
        query['author'] = params['author']
    if 'source' in params:
        query['source'] = params['source']
    if 'min_views' in params and 'max_views' in params:
        query['num_views'] = {"$gte": params['min_views'], "$lte": params['max_views']}
    if 'min_comments' in params and 'max_comments' in params:
        query['num_comments'] = {"$gte": params['min_comments'], "$lte": params['max_comments']}
    if 'datecreated_start' in params and 'datecreated_end' in params:
        query['datecreated'] = {"$gte": params['datecreated_start'], "$lte": params['datecreated_end']}
    if 'length_min' in params and 'length_max' in params:
        query['length'] = {"$gte": params['length_min'], "$lte": params['length_max']}
    if 'title' in params:
        query['title'] = params['title']
    if 'hashtags' in params:
        query['hashtags'] = {"$in": params['hashtags']}
    if 'botid' in params:
        query['botid'] = params['botid']

    return list(collection.find(query))
