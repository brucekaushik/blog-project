import webapp2
import hmac
import os
from BaseHandler import BaseHandler
from helpers import BlogHelper
from helpers import UserHelper
from models import User

current_path = os.getcwd()
file_path = current_path + '/secret.txt'
SECRET = open(file_path, 'r').read()


class BlogHandler(BaseHandler):

    '''
    base handler for blog,
    methods specific to blog functionality are defined here
    '''

    def initialize(self, *a, **kw):
        '''
        initialilze method runs on very request
        (google app engine gets called)
        '''
        webapp2.RequestHandler.initialize(
            self, *a, **kw)  # required, don't know why

        user_id = self.get_cookie('user_id')
        self.user = user_id and UserHelper.get_user_by_id(int(user_id))

    def set_cookie(self, cookie_name, cookie_val):
        '''
        set cookie cookie name and value
        '''

        # secure cookie value
        cookie_val = BlogHelper.secure_cookie_val(cookie_val)

        # set cookie by adding a http header
        self.response.headers.add_header(
            'Set-Cookie', '%s=%s; Path=/' % (cookie_name, cookie_val))

    def get_cookie(self, cookie_name):
        '''
        get cookie value by using cookie name
        '''
        cookie_val = self.request.cookies.get(cookie_name)
        return cookie_val and BlogHelper.verify_secure_cookie_val(cookie_val)

    def login(self, user):
        '''
        login user by setting cookie
        user = user object
        '''
        self.set_cookie('user_id', user.key().id())

    def logout(self):
        '''
        logout user by clearing cookie
        '''
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def register(self, username, password, email=None):
        '''
        register user (does not store in db)
        '''

        # hash password to store in db
        password_hash = BlogHelper.hash_str(password)

        # create and return user (this does not update database)
        return User(parent=UserHelper.get_users_key(),
                    username=username,
                    password_hash=password_hash,
                    email=email)
