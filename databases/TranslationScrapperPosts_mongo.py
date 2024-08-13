from pymongo import MongoClient, ASCENDING
from bson.objectid import ObjectId
from utils import load_json
from datetime import datetime

config = load_json()

# Connect to MongoDB
client_name = config['botid']
connection_string = config['database']['connection_string']
database_name = config['database']['name']

client = MongoClient(connection_string)
db = client[database_name]
collection = db['TranslationScrapperPosts']

# Ensure indexes
collection.create_index([("id", ASCENDING)], unique=True)
collection.create_index("link")
collection.create_index("account")
collection.create_index("destination")
collection.create_index("botid")
collection.create_index("video_id")

def insert_translation_scrapper_post(link, account, destination, num_comments, num_likes, num_views, length, video_id, translated, captions, tts_settings, botid):
    post = {
        "link": link,
        "account": account,
        "destination": destination,
        "num_comments": num_comments,
        "num_likes": num_likes,
        "num_views": num_views,
        "datecreated": datetime.now(),
        "length": length,
        "video_id": ObjectId(video_id),  # Reference to the ScrapedVideos collection
        "translated": translated,
        "captions": captions,  # Expected to be a dictionary with the relevant params
        "tts_settings": tts_settings,  # Expected to be a dictionary with the relevant params
        "botid": botid
    }
    return collection.insert_one(post).inserted_id

# Getters
def get_post_by_id(post_id):
    return collection.find_one({"_id": ObjectId(post_id)})

def get_post_by_link(link):
    return collection.find_one({"link": link})

def get_posts_by_account(account):
    return list(collection.find({"account": account}))

def get_posts_by_destination(destination):
    return list(collection.find({"destination": destination}))

def get_posts_by_botid(botid):
    return list(collection.find({"botid": botid}))

def get_posts_by_video_id(video_id):
    return list(collection.find({"video_id": ObjectId(video_id)}))

# Search by Multiple Parameters
def search_posts(params):
    query = {}
    if 'account' in params:
        query['account'] = params['account']
    if 'destination' in params:
        query['destination'] = params['destination']
    if 'min_views' in params and 'max_views' in params:
        query['num_views'] = {"$gte": params['min_views'], "$lte": params['max_views']}
    if 'min_comments' in params and 'max_comments' in params:
        query['num_comments'] = {"$gte": params['min_comments'], "$lte": params['max_comments']}
    if 'datecreated_start' in params and 'datecreated_end' in params:
        query['datecreated'] = {"$gte": params['datecreated_start'], "$lte": params['datecreated_end']}
    if 'length_min' in params and 'length_max' in params:
        query['length'] = {"$gte": params['length_min'], "$lte": params['length_max']}
    if 'translated' in params:
        query['translated'] = params['translated']
    if 'video_id' in params:
        query['video_id'] = ObjectId(params['video_id'])

    return list(collection.find(query))
