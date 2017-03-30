from google.appengine.ext import db
from models.Like import Like

def get_likes_key(name='default'):
    '''
    define a parent group 'likes' identified by 'default'
    useful for attaching data of all likes
    '''
    return db.Key.from_path('likes', name)

def get_like_by_id(like_id):
    '''
    get like object by like id
    '''
    return Like.get_by_id(int(like_id), parent=get_likes_key())

def get_postlikes_by_username(post_id, username):
    '''
    get likes of post by username and post_id
    '''
    post_id = str(post_id)
    username = str(username)
    likes = Like.all().filter('username = ', username).filter(
        'post_id = ', post_id).ancestor(get_likes_key())
    return likes

def get_likes_count_for_post(post_id):
    '''
    get likes count for a post
    '''
    post_id = str(post_id)
    likes = Like.all().filter(
        'post_id = ', post_id).ancestor(get_likes_key())
    return likes.count()

def like_exists(like_id):
    '''
    return like if it exists
    '''
    key = db.Key.from_path('likes', int(like_id))
    like = db.get(key)
    if like:
        return like