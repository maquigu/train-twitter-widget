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
import tcelery, tasks

tcelery.setup_nonblocking_producer()

class WSListFeedHandler(WebSocketHandler):
    Twitter = None
    owner_screen_name = None
    slug = None
    new_feed_on = False
    max_id = None
    since_id = None

    @staticmethod
    def url():
        return r'/ws-list-feed/([^/]+)/([^/]+)'
    
    def check_origin(self, origin):
        return True

    def open(self, owner_screen_name, slug):
        log.info("Connected: %r" % self.request)
        self.owner_screen_name = owner_screen_name
        self.slug = slug
        return

    def on_message(self, message):
        log.debug('Message: %r' % message)
        log.debug('Feed On: %r' % self.new_feed_on)
        cursor = json_decode(message)
        if 'remove_tweet' in cursor:
            log.debug('Removing tweet id %s from %s %s' % (cursor['remove_tweet'], self.owner_screen_name, self.slug))
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
                self.owner_screen_name,
                self.slug,
                self.since_id,
                None,
                config.tweet_count,
            )
            log.debug('Retrieving new: %r' % repr(args))
            ret = tasks.get_list_statuses.apply_async(args, callback=self.on_list_statuses_return)
            log.debug('Return from Apply Async: %r' % ret)
        elif cursor['direction'] == 'old':
            #self.new_feed_on = False
            log.debug('Checking for old messages ...')
            args = (
                cursor['direction'],
                self.owner_screen_name,
                self.slug, 
                None,
                self.max_id,
                config.tweet_count,
            )
            ret = tasks.get_list_statuses.apply_async(args, callback=self.on_list_statuses_return)
            log.debug('Return from Apply Async: %r' % ret)
        else:
            log.warning('Cannot process: %r' % self.request)
        return

    def on_list_statuses_return(self, response):
        log.debug('Returning from Celery: %r' % response)
        statuses = response.result['statuses']
        direction = response.result['direction']
        if direction == 'new':
            if len(statuses) > 0:
                self.max_id = statuses[-1]['id']
                self.since_id = statuses[0]['id']
                message = {
                    'statuses': statuses,
                    'direction': direction
                }
                log.debug('Sending: %r' % len(statuses))
                log.debug('Max: %r, Since: %r' % (self.max_id, self.since_id))
                self.write_message(json_encode(message))
            else:
                log.debug('Nothing to send: %r' % len(statuses))
            if self.new_feed_on is True:
                args = (
                        direction,
                        self.owner_screen_name,
                        self.slug,  
                        self.since_id,
                        self.max_id,
                        config.tweet_count,
                )
                ret = tasks.get_list_statuses.apply_async(args, callback=self.on_list_statuses_return, countdown=config.poll_interval)
                log.debug('Return from Apply Async: %r' % ret)
        if direction == 'old':
                if len(statuses) > 0:
                    self.max_id = statuses[-1]['id']
                    log.debug('Max, Since: %r, %r' % (self.max_id, self.since_id))
                    message = {
                        'statuses': statuses,
                        'direction': direction
                    }
                    log.debug('Sending: %r' % len(statuses))
                    self.write_message(json_encode(message))
                else:
                    log.debug('Nothing to send: %r' % len(statuses))

