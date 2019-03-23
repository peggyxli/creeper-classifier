from app import app
import sys
import praw
import os
from google.cloud import vision

reddit = praw.Reddit(client_id=app.config['REDDIT_CLIENT_ID'],
                     client_secret=app.config['REDDIT_CLIENT_SECRET'],
                     user_agent=app.config['REDDIT_USER_AGENT'])

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = app.config['GOOGLE_CREDENTIALS_PATH']


def scraper_run_func():
    for submission in reddit.subreddit('creepyPMs').top('all', limit=1):
        print(submission.title, file=sys.stderr)
        print(submission.url, file=sys.stderr)
        file_extension = submission.url[-4:]
        if not (file_extension == '.jpg' or file_extension == '.png'):
            print ('Unrecognized file type')
        else:
            print ('Sending to Google')
            detect_text_uri(submission.url)
        print('-------------', file=sys.stderr)


def detect_text_uri(uri):
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image()
    image.source.image_uri = uri

    response = client.text_detection(image=image)
    text = response.text_annotations[0].description.replace('\n', ' ')
    print(text)
