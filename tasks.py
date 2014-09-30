import time
from datetime import datetime
from twitter import *
from config import config
from celery import Celery
from pprint import pprint

celery = Celery("tasks", broker="amqp://guest:guest@localhost:5672")
celery.conf.CELERY_RESULT_BACKEND = "amqp"
auth = OAuth(config.access_key, config.access_secret, config.consumer_key, config.consumer_secret)
twitter = Twitter(auth = auth)

@celery.task
def get_list_statuses(direction, owner_screen_name, slug, since_id=None, max_id=None, tweet_count=config.tweet_count):
    tw_kwargs = {
        'owner_screen_name':owner_screen_name,
        'slug':slug,
        'count':tweet_count,
    }
    if since_id is not None:
        tw_kwargs['since_id']=since_id
    if max_id is not None:
        tw_kwargs['max_id']=max_id
    pprint('Fetching list: %r' % tw_kwargs)
    statuses = twitter.lists.statuses(**tw_kwargs)
    return {
        'direction': direction,
        'statuses': statuses
    }
    
