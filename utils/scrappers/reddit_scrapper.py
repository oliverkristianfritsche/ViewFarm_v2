import praw
import os
from dotenv import load_dotenv
from pathlib import Path
import json

config_path = '/root/config.json'

config = json.load(open(config_path, 'r'))


def init_reddit_client():
    return praw.Reddit(
        client_id=config['CLIENT_ID'],
        client_secret=config['CLIENT_SECRET'],
        user_agent=config['USER_AGENT']
    )

def get_top_n_hot_threads(reddit, subreddit_name, n):
    subreddit = reddit.subreddit(subreddit_name)
    hot_threads = subreddit.hot(limit=n+1)

    top_threads = []
    for submission in hot_threads:
        top_threads.append({
            'title': submission.title,
            'author': submission.author.name if submission.author else 'N/A',
            'score': submission.score,
            'url': submission.url,
            'num_comments': submission.num_comments,
            'id': submission.id
        })

    return top_threads[1:]

def get_post_details(reddit, post_id):
    submission = reddit.submission(id=post_id)
    return {
        'title': submission.title,
        'body': submission.selftext
    }