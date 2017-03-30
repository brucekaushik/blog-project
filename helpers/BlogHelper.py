import re
import hmac
import os

current_path = os.getcwd()
file_path = current_path + '/secret.txt'
SECRET = open(file_path,'r').read()

def blog_key(name='default'):
        '''
        define a parent (blog name) for all of our blog data
        '''
        return db.Key.from_path('blogs', name)
        # this is getting a random key based on the text 'blogs'
        # change blogs to something else and the key is changing
        # call this function and print the key to observe this
        # https://cloud.google.com/appengine/docs/standard/python/datastore/keyclass
        # here, blogs is 'kind' name
        # and name(default) is the identifier name (can be group as per our
        # design)

def validate_username(username):
        user_regex = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        return username and user_regex.match(username)

def validate_password(password):
        password_regex = re.compile(r"^.{3,20}$")
        return password and password_regex.match(password)

def validate_email(email):
        email_regex = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
        return not email or email_regex.match(email)

def hash_str(string_to_hash):
        '''
        hash string by using hmac & secret
        '''
        string_to_hash = str(string_to_hash)
        return hmac.new(SECRET, string_to_hash).hexdigest()
        # return hashlib.md5(string_to_hash).hexdigest()

def secure_cookie_val(cookie_val):
        cookie_val = "%s|%s" % (cookie_val, hash_str(cookie_val))
        return cookie_val

def verify_secure_cookie_val(cookie_val):
        cookie_actual_val = cookie_val.split("|")[0]
        if cookie_val == secure_cookie_val(cookie_actual_val):
                return cookie_actual_val