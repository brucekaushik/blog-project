from google.appengine.ext import db
from handlers import BaseHandler
from helpers import LikeHelper
from helpers import CommentHelper

class Post(db.Model):
    '''
    Post entity
    '''

    username = db.StringProperty(required=True)
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now_add=True)

        

        