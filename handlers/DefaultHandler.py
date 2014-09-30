import traceback
import logging as log
from tornado.web import RequestHandler
from tornado.escape import json_decode
from tornado.escape import json_encode

class DefaultHandler(RequestHandler):

    db_users = None

    def initialize(self):
        pass # DB init, etc.

    @staticmethod
    def url():
        return r'/'

    def post(self):
        self.get()

    def get(self):
        #self.write('Hello, World!')
        self.render('../static/index.html')


