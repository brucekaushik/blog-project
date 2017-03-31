from google.appengine.ext import db


class User(db.Model):

    '''
    User entity
    '''

    username = db.StringProperty(required=True)
    password_hash = db.StringProperty(required=True)
    email = db.StringProperty()
