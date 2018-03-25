#!/usr/bin/env python3

import bcrypt
from prompt_toolkit import prompt
from sqlalchemy import create_engine
from tornado import escape
from sqlalchemy.orm import sessionmaker

from settings import settings
from apps.main.models import UserModel
from utils import make_session

def main():
    with make_session() as session:
        username = prompt('Enter username: ')
        password = escape.utf8(prompt('Enter password: '))

        user = UserModel(name=username, password=bcrypt.hashpw(password, bcrypt.gensalt()))
        session.add(user)
        session.commit()
        session.close()

if __name__ == '__main__':
    main()
