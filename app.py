#!/usr/bin/env python3

import tornado.ioloop
from tornado.ioloop import IOLoop
import tornado.web
from tornado.options import options
from settings import settings
from urls import url_patterns

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

def make_app():
    return tornado.web.Application(url_patterns, **settings)

def main():
    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    server.bind(options.port)
    server.start(0)
    IOLoop.current().start()

if __name__ == '__main__':
    main()
