import time
from datetime import datetime
from config import config
from celery import Celery
from pprint import pprint
import requests

celery = Celery("tasks", broker="amqp://guest:guest@localhost:5672")
celery.conf.CELERY_RESULT_BACKEND = "amqp"

@celery.task
def get_stream_tweets(direction, stream_name, since_id=None, max_id=None, tweet_count=config.tweet_count):
    params = {
        'direction': direction,
        'stream_name': stream_name,
        'count': tweet_count,
    }
    if since_id is not None:
        params['since_id']=since_id
    if max_id is not None:
        params['max_id']=max_id
    pprint('Fetching list: %r' % params)
    r = requests.get('http://localhost:8080/streams/%s/tweets' % stream_name, params=params)
    if r.status_code == 200:
        response = r.json()
    return response
