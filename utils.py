from contextlib import contextmanager

from sqlalchemy import create_engine
from tornado import escape
from sqlalchemy.orm import sessionmaker
from settings import settings


class LoginFailed(Exception):
    pass

@contextmanager
def make_session():
    try:
        engine = create_engine(settings['db'])
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
    finally:
        session.close()
