import bcrypt
import tornado.escape as escape
from tornado.web import RequestHandler
from tornado.web import create_signed_value
from settings import settings
from utils import make_session
from utils import LoginFailed

from .models import UserModel


class LoginRequiredView(RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")


class LogoutView(RequestHandler):
    def get(self):
        self.clear_cookie("username")
        self.redirect(self.get_argument("next", "/"))


class LoginView(LoginRequiredView):
    """
    Реализация логина
    """
    def get(self):
        self.render('login.html')

    def post(self):
        fields = [
            'username',
            'password'
        ]

        username, password = [self.get_argument(arg) for arg in fields]

        if not (username and password):
            raise LoginFailed('User and password are required')

        with make_session() as session:
            q = session.query(UserModel)
            user = q.filter_by(name=username).first()

        if not user:
            raise LoginFailed('No such user')

        if not bcrypt.checkpw(escape.utf8(password), user.password):
            raise LoginFailed('Password')

        self.set_header('Content-Type', 'application/json')
        cookie = self.create_signed_value('username', username)
        self.write({"token": cookie.decode()})
