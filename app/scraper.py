from app import app
import sys
import praw

reddit = praw.Reddit(client_id=app.config['REDDIT_CLIENT_ID'],
                     client_secret=app.config['REDDIT_CLIENT_SECRET'],
                     user_agent=app.config['REDDIT_USER_AGENT'])

def scraper_run_func():
    for submission in reddit.subreddit('creepyPMs').top('all', limit=100):
        print(submission.title, file=sys.stderr)
        print(submission.url, file=sys.stderr)
        file_extension = submission.url[-4:]
        if not (file_extension == '.jpg' or file_extension == '.png'):
            print ('Unrecognized file type')
        else:
            print ('Sending to Google')
        print('-------------', file=sys.stderr)
