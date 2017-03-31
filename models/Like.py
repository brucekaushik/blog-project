from google.appengine.ext import db


class Like(db.Model):

    '''
    Post entity
    '''

    post_id = db.StringProperty(required=True)
    username = db.StringProperty(required=True)
    like = db.BooleanProperty()
