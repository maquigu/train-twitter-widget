import traceback
import logging as log
from config import config
from tornado.web import RequestHandler
from tornado.escape import json_decode
from tornado.escape import json_encode
from twitter import *

class GetFeedHandler(RequestHandler):

    db_users = None

    def initialize(self):
        pass # DB init, etc.

    @staticmethod
    def url():
        return r'/get-list-feed/([^/]+)/([^/]+)'

    def post(self):
        self.get()

    def get(self, owner_screen_name, slug):
        auth = OAuth(config.access_key, config.access_secret, config.consumer_key, config.consumer_secret)
        twitter = Twitter(auth = auth)
        statuses = twitter.lists.statuses(owner_screen_name=owner_screen_name, slug=slug, count=30)
        self.write(json_encode(statuses))
