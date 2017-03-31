from google.appengine.ext import db


class Comment(db.Model):

    '''
    Comment entity
    '''

    post_id = db.StringProperty(required=True)
    username = db.StringProperty(required=True)
    comment = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now_add=True)
