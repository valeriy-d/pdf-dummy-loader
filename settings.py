# std
import os
import logging.config
from collections import namedtuple

import tornado
from tornado.options import define, options

define("port", default=8001, type=int)
define("debug", default=False, type=bool)

options.parse_command_line()

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

db = namedtuple('db', 'name location engine')
db = db(
    name="dummy.db",
    location=PROJECT_ROOT,
    engine='sqlite:///'
)

template_path = os.path.join(PROJECT_ROOT, 'templates')

settings = {
    'debug': options.debug,
    'static_path': os.path.join(PROJECT_ROOT, 'static'),
    'login_url': r'/login',
    'template_path': template_path,
    'cookie_secret': "DZ4jH93kQFe7LqEgzdUe0aSpIxNCbUXmmENuocbbmcw=",
    'cookie_expires': 8,
    'name': True,
    'db': ''.join([db.engine, os.path.join(db.location, db.name)]),
    'upload_path': 'storage'
}
