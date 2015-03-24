#!/usr/bin/python

import sys, os
from config import config
import logging as log
import tornado.ioloop
import tornado.httpserver
import tornado.web
from WebService import WebService

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

log.basicConfig(filename= config.name + '.log',level=log.DEBUG)

handler_urls = WebService.load_handlers(config.root_dir)
handler_urls.append((r'/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'}))
for tup in  handler_urls:
    print tup

application = tornado.web.Application(handler_urls)
if __name__ == '__main__':
    #http_server = tornado.httpserver.HTTPServer(application, ssl_options={
    #    "certfile": "server.crt",
    #    "keyfile": "server.key",
    #})
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(config.port)
    tornado.ioloop.IOLoop.instance().start()
