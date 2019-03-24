from flask import jsonify, abort, make_response, request
from app import app
from .scraper import scraper_run_func
import dialogflow_v2 as dialogflow

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"


tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]


@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': tasks}), 201


@app.route('/api/scraper', methods=['POST'])
def run_scraper():
    if not request.json or not 'subreddit_name' in request.json or not 'intent_name' in request.json:
        abort(400)
    scraper_run_func(request.json['subreddit_name'], request.json['intent_name'])
    return jsonify({'response': 'scraper has finished'}), 201


@app.route('/api/test_message', methods=['POST'])
def test_message():
    if not request.json or not 'email' in request.json or not 'message' in request.json:
        abort(400)

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(app.config['CLASSIFIER_PROJECT_ID'], request.json['email'])
    print('Session path: {}\n'.format(session))

    text_input = dialogflow.types.TextInput(text=request.json['message'], language_code='en')
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = session_client.detect_intent(session=session, query_input=query_input)

    return jsonify({'response': response.query_result.fulfillment_text, 'match': response.query_result.intent_detection_confidence}), 201


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
