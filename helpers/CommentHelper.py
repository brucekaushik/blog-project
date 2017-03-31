from google.appengine.ext import db
from models.Comment import Comment


def get_comments_key(name='default'):
    '''
    define a parent group 'comments' identified by 'default'
    useful for attaching data of all comments
    '''
    return db.Key.from_path('comments', name)


def get_comments_for_post(post_id):
    '''
    get all comments for a post
    '''
    post_id = str(post_id)
    comments = Comment.all().filter(
        'post_id = ', post_id).ancestor(get_comments_key())
    return comments


def get_comment_by_id(comment_id):
    '''
    get comment object by comment id
    '''
    return Comment.get_by_id(
        int(comment_id),
        parent=get_comments_key()
    )
