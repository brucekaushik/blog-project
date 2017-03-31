from models import User
from google.appengine.ext import db
import BlogHelper


def get_users_key(name='default'):
    '''
    define a parent group 'users' identified by 'default',
    useful for attaching data of all users
    '''
    return db.Key.from_path('users', name)


def get_user_by_id(user_id):
    '''
    get user object by user id
    '''
    return User.get_by_id(user_id, parent=get_users_key())
    # note: get_by_id is data store build in method


def get_user_by_name(username):
    '''
    get user object by username name
    '''
    return User.all().filter('username = ', username).get()


def validate_db_password(username, password, password_hash):
    '''
    validate password from db with password hash
    '''
    password = BlogHelper.hash_str(password)
    return password == password_hash


def login(username, password):
    '''
    return user object for logging in
    '''
    # get user by username
    user = get_user_by_name(username)

    # validate password if user exists
    # return user if validation is successful
    if user and validate_db_password(
        username,
        password,
        user.password_hash
    ):
        return user
