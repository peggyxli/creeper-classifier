from app import app
import sys
import praw
import os
from google.cloud import vision
import dialogflow_v2 as dialogflow

reddit = praw.Reddit(client_id=app.config['REDDIT_CLIENT_ID'],
                     client_secret=app.config['REDDIT_CLIENT_SECRET'],
                     user_agent=app.config['REDDIT_USER_AGENT'])

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = app.config['GOOGLE_CREDENTIALS_PATH']


def scraper_run_func(subreddit_name, intent_name, response_message):
    print (intent_name)
    training_phrases = []

    for submission in reddit.subreddit(subreddit_name).top('all', limit=100):
        print(submission.title, file=sys.stderr)
        print(submission.url, file=sys.stderr)
        file_extension = submission.url[-4:]

        if not (file_extension == '.jpg' or file_extension == '.png'):
            print ('Unrecognized file type')
        else:
            print ('Sending to Google')
            image_text = detect_text_uri(submission.url)
            if len(image_text) > 0:
                print (image_text)
                part = dialogflow.types.Intent.TrainingPhrase.Part(text=image_text[:768])
                training_phrase = dialogflow.types.Intent.TrainingPhrase(parts=[part])
                training_phrases.append(training_phrase)
            else:
                print ('Error: No text found')
        print('-------------', file=sys.stderr)

    if len(training_phrases) > 0:
        message_arr = []
        message_arr.append('Warning: ' + response_message)
        create_intent(intent_name, training_phrases, message_arr)
    return


def detect_text_uri(uri):
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image()
    image.source.image_uri = uri

    response = client.text_detection(image=image)
    if len(response.text_annotations) > 0:
        text = response.text_annotations[0].description.replace('\n', ' ')
        return text.strip()
    else:
        return ''


def create_intent(my_display_name, training_phrases, message_texts):
    intents_client = dialogflow.IntentsClient()
    parent = intents_client.project_agent_path(app.config['CLASSIFIER_PROJECT_ID'])

    my_intents = intents_client.list_intents(parent)
    for element in my_intents:
        if element.display_name == my_display_name:
            intents_client.delete_intent(element.name)
        pass

    text = dialogflow.types.Intent.Message.Text(text=message_texts)
    message = dialogflow.types.Intent.Message(text=text)

    intent = dialogflow.types.Intent(
        display_name=my_display_name,
        training_phrases=training_phrases,
        messages=[message])

    response = intents_client.create_intent(parent, intent)
    print('Intent created: {}'.format(response))
