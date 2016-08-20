import traceback
import inspect
import time
import logging as log
from config import config
from tornado.websocket import WebSocketHandler
from tornado.escape import json_decode
from tornado.escape import json_encode
from twitter import *
from tornado import gen, web
import tcelery, widget_tasks

tcelery.setup_nonblocking_producer()

class WSStreamFeedHandler(WebSocketHandler):
    Twitter = None
    stream_name = None
    new_feed_on = False
    max_id = None
    since_id = None

    @staticmethod
    def url():
        return r'/ws-stream-feed/([^/]+)'
    
    def check_origin(self, origin):
        return True

    def open(self, stream_name):
        log.info("Connected: %r" % self.request)
        self.stream_name = stream_name
        return

    def on_message(self, message):
        log.debug('Message: %r' % message)
        log.debug('Feed On: %r' % self.new_feed_on)
        cursor = json_decode(message)
        if 'remove_tweet' in cursor:
            log.debug('Removing tweet id %s from %s Stream' % (cursor['remove_tweet'], self.stream_name))
            #ret = widget_tasks.remove_tweet.apply_async(args, queue=config.celery_queue, callback=self.on_remove_tweet_return) 
            self.write_message(json_encode({'removed': 'OK'}))
            return
        if cursor['direction'] == 'new':
            if self.new_feed_on is False:
                self.new_feed_on = True 
            else: 
                return
            log.debug('Checking for new messages ...')
            args = (
                cursor['direction'],
                self.stream_name,
                self.since_id,
                None,
                config.tweet_count,
            )
            log.debug('Retrieving new: %r' % repr(args))
            ret = widget_tasks.get_stream_tweets.apply_async(args, queue=config.celery_queue, callback=self.on_stream_tweets_return)
            log.debug('Return from Apply Async: %r' % ret)
        elif cursor['direction'] == 'old':
            #self.new_feed_on = False
            log.debug('Checking for old messages ...')
            args = (
                cursor['direction'],
                self.stream_name,
                None,
                self.max_id,
                config.tweet_count,
            )
            ret = widget_tasks.get_stream_tweets.apply_async(args, queue=config.celery_queue, callback=self.on_stream_tweets_return)
            log.debug('Return from Apply Async: %r' % ret)
        else:
            log.warning('Cannot process: %r' % self.request)
        return

    def on_stream_tweets_return(self, response):
        log.debug('Returning from Celery: %r' % response)
        tweets = response.result['tweets']
        direction = response.result['direction']
        if direction == 'new':
            if len(tweets) > 0:
                self.max_id = tweets[-1]['id']
                self.since_id = tweets[0]['id']
                message = {
                    'tweets': tweets,
                    'direction': direction
                }
                log.debug('Sending: %r' % len(tweets))
                log.debug('Max: %r, Since: %r' % (self.max_id, self.since_id))
                self.write_message(json_encode(message))
            else:
                log.debug('Nothing to send: %r' % len(tweets))
            if self.new_feed_on is True:
                args = (
                        direction,
                        self.stream_name,
                        self.since_id,
                        self.max_id,
                        config.tweet_count,
                )
                ret = tasks.get_stream_tweets.apply_async(args, queue=config.celery_queue, callback=self.on_stream_tweets_return, countdown=config.poll_interval)
                log.debug('Return from Apply Async: %r' % ret)
        if direction == 'old':
                if len(tweets) > 0:
                    self.max_id = tweets[-1]['id']
                    log.debug('Max, Since: %r, %r' % (self.max_id, self.since_id))
                    message = {
                        'tweets': tweets,
                        'direction': direction
                    }
                    log.debug('Sending: %r' % len(tweets))
                    self.write_message(json_encode(message))
                else:
                    log.debug('Nothing to send: %r' % len(tweets))

