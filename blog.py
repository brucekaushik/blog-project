# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import jinja2
import webapp2
import hashlib
import hmac
import random
import string
import re

from google.appengine.ext import db

# build path to templates directory
template_dir = os.path.join(os.path.dirname(__file__),"templates")
# initialize jinja environment
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

# define a secret key
SECRET = 'my secret, which is not so secret'


class BaseHandler(webapp2.RequestHandler):
    '''
    inherit from this handler to access commonly used methods
    '''

    def write(self, *a, **kw):
        '''
        shorcut to using self.response.out.write everytime
        '''
        self.response.out.write( *a, **kw)

    def render_str(self, template, **params):
        '''
        return html output to render, as a string
        '''
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        '''
        render html
        '''
        self.response.out.write(self.render_str(template, **kw))

class BlogHandler(BaseHandler):
    '''
    base handler for blog, methods specific to blog functionality are defined here
    '''

    def initialize(self, *a, **kw):
        '''
        initialilze method runs on very request (google app engine gets called)
        '''
        webapp2.RequestHandler.initialize(self, *a, **kw) # required, don't know why
        
        user_id = self.get_cookie('user_id')
        self.user = user_id and User.get_user_by_id(int(user_id))

    def blog_key(self, name = 'default'):
        '''
        define a parent (blog name) for all of our blog data
        '''
        return db.Key.from_path('blogs', name)
        # this is getting a random key based on the text 'blogs'
        # change blogs to something else and the key is changing
        # call this function and print the key to observe this
        # https://cloud.google.com/appengine/docs/standard/python/datastore/keyclass
        # here, blogs is 'kind' name
        # and name(default) is the identifier name (can be group as per our design)

    def set_cookie(self, cookie_name, cookie_val):
        cookie_val = BlogHandler.secure_cookie_val(cookie_val)

        # set cookie by adding a http header
        self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (cookie_name, cookie_val))

    def get_cookie(self, cookie_name):
        cookie_val = self.request.cookies.get(cookie_name)
        return cookie_val and BlogHandler.verify_secure_cookie_val(cookie_val)

    def login(self, user):
        '''
        user = user object
        '''
        self.set_cookie('user_id', user.key().id())

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def register(self, username, password, email = None):
        # hash password
        password_hash = BlogHandler.hash_str(password)

        # create and return user (this does not update database)
        return User(parent = User.get_users_key(), username = username, password_hash = password_hash, email = email)

    @classmethod
    def validate_username(cls, username):
        user_regex = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        return username and user_regex.match(username)

    @classmethod
    def validate_password(cls, password):
        password_regex = re.compile(r"^.{3,20}$")
        return password and password_regex.match(password)

    @classmethod
    def validate_email(cls, email):
        email_regex  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
        return not email or email_regex.match(email)

    @classmethod
    def hash_str(cls, string_to_hash):
        string_to_hash = str(string_to_hash)
        return hmac.new(SECRET, string_to_hash).hexdigest()
        # return hashlib.md5(string_to_hash).hexdigest()

    @classmethod
    def secure_cookie_val(cls, cookie_val):
        cookie_val = "%s|%s" % (cookie_val, BlogHandler.hash_str(cookie_val))
        return cookie_val

    @classmethod
    def verify_secure_cookie_val(self, cookie_val):
        cookie_actual_val = cookie_val.split("|")[0]
        if cookie_val == BlogHandler.secure_cookie_val(cookie_actual_val):
            return cookie_actual_val

class BlogFront(BlogHandler):
    '''
    blog front page, with recent 10 posts
    '''

    def get(self):
        '''
        get 10 recent posts from Post entity and render them using front.html
        '''
        posts = db.GqlQuery("select * from Post order by created desc limit 10")
        self.render('front.html', posts = posts, user = self.user)

class Signup(BlogHandler):
    '''
    handle signups here
    '''

    def get(self):
        self.render("signup-form.html", user = self.user)

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(username = username,
                      email = email)

        if not BlogHandler.validate_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not BlogHandler.validate_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True

        elif password != verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not BlogHandler.validate_email(email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', user = self.user, **params)
        else:
            user = self.register(username, password, email)
            user_check = User.check_user_exists(user)
            if user_check:
                params['error_username'] = "User already exists! Please enter a unique username."
                self.render('signup-form.html', user = self.user, **params)
            else:
                user.put()
                self.login(user)
                self.redirect('/')

class User(db.Model, BlogHandler):
    """ User entity in datastore """

    username = db.StringProperty(required = True)
    password_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def get_users_key(cls, name = 'default'):
        '''
        define a parent group 'users' identified by 'default' 
        useful for attaching data of all users
        '''
        return db.Key.from_path('users', name)

    @classmethod
    def get_user_by_id(cls, user_id):
        return User.get_by_id(user_id, parent = User.get_users_key())
        # get_by_id is data store build in method

    @classmethod
    def get_user_by_name(cls, username):
        user = User.all().filter('username = ', username).get()
        return user

    @classmethod
    def check_user_exists(cls, user):
        u = User.get_user_by_name(user.username)
        if u:
            return u

    @classmethod
    def validate_db_password(cls, username, password, password_hash):
        password = BlogHandler.hash_str(password)
        return password == password_hash

    @classmethod
    def login(cls, username, password):
        user = cls.get_user_by_name(username)
        if user and cls.validate_db_password(username, password, user.password_hash):
            return user

class Login(BlogHandler):
    
    def get(self):
        self.render('login-form.html', user = self.user)

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')

        if not BlogHandler.validate_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not BlogHandler.validate_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True

        if have_error:
            self.render('login-form.html', **params)
        else:
            user = User.login(username, password)
            self.login(user)
            self.redirect('/')
                

class Logout(BlogHandler):
    
    def get(self):
        self.logout();
        self.redirect('/')
        
class Post(db.Model, BlogHandler):
    '''
    Post entity in data store
    '''

    username = db.StringProperty(required = True)
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now_add = True)

    def render(self, session_user = False):
        '''
        render blog post
        '''

        # get likes
        likes = Like.get_likes(self.key().id(), session_user.username)
       
        # get latest like id (in case post got liked by the same user multiple times)
        if likes.count():
            like_id = likes[0].key().id()
        else:
            like_id = 0

        # get likes count
        likes_count = Like.get_likes_count(self.key().id())

        self._render_text = self.content.replace('\n','<br>')
        return self.render_str("post.html", p = self, like_id = like_id, likes_count = likes_count)

    @classmethod
    def get_posts_key(cls, name = 'default'):
        '''
        define a parent group 'posts' identified by 'default' 
        useful for attaching data of all posts
        '''
        return db.Key.from_path('posts', name)

    

class NewPost(BlogHandler):
    '''
    Handle new posts (submission & redirect)
    '''

    def get(self):
        '''
        render new post form
        '''
        if self.user:
            self.render("newpost.html", user = self.user)
        else:
            self.render('login-form.html', user = self.user)

    def post(self):
        if self.user:
            # get request params
            username = self.user.username
            subject = self.request.get('subject')
            content = self.request.get('content')

            # if username, subject and contents are proper, put on db and redirect
            # else render form with error
            if username and subject and content:
                p = Post(parent = Post.get_posts_key(), username = username, subject = subject, content = content)
                p.put()
                self.redirect('/post/%s' % str(p.key().id()))
            else:
                error = "subject and content, please!"
                self.render("newpost.html", user = self.user, subject=subject, content=content, error=error)

class PostPage(BlogHandler):
    '''
    Handle Post Page (permalink)
    '''

    def get(self, post_id):
        '''
        get post from database and render it using template
        '''

        # get the post key
        key = db.Key.from_path('Post', int(post_id), parent = Post.get_posts_key())
        # get the post from db using key
        post = db.get(key)

        # show 404 if post is not available
        if not post:
            self.error(404)
            self.write('Error! Post Not Found')
            return

        # render post using permalink template
        # notice that post will have a render method (see definition) which will also be availble in jinja
        self.render("permalink.html", post = post, user = self.user)

class EditPost(BlogHandler):
    '''
    Handle new posts (submission & redirect)
    '''

    def get(self, post_id):
        '''
        render new post form
        '''
        if self.user:

            post = Post.get_by_id(int(post_id), parent = Post.get_posts_key())
            post.content = post.content.replace('<br>','\n')

            if self.user.username != post.username:
                error = "not your post to edit!"
                self.render("permissiondenied.html", error=error, user = self.user)
                return

            self.render("editpost.html", user = self.user, post = post)
        else:
            self.redirect('/login')

    def post(self, post_id):
        if self.user:
            # get request params
            username = self.user.username
            subject = self.request.get('subject')
            content = self.request.get('content')

            post = Post.get_by_id(int(post_id), parent = Post.get_posts_key())
            post.subject = subject
            post.content = content.replace('\n','<br>')

            # if username, subject and contents are proper, put on db and redirect
            # else render form with error
            if username and subject and content:
                if username == post.username:
                    post.put()
                    self.redirect('/post/%s' % str(post_id))
                else:
                    error = "not your post to edit!"
                    self.render("permissiondenied.html", error=error, user = self.user)
            else:
                error = "subject and content, please!"
                self.render("newpost.html", user = self.user, subject=subject, content=content, error=error)

class DeletePost(BlogHandler):
    '''
    Handle new posts (submission & redirect)
    '''

    def get(self, post_id):
        '''
        render delete post form
        '''
        if self.user:

            post = Post.get_by_id(int(post_id), parent = Post.get_posts_key())
            post.content = post.content.replace('<br>','\n')

            if self.user.username != post.username:
                error = "not your post to delete!"
                self.render("permissiondenied.html", error=error, user = self.user)
                return

            self.render("deletepost.html", user = self.user, post = post)
        else:
            self.redirect('/login')

    def post(self, post_id):
        if self.user:
            # get request params
            username = self.user.username
            subject = self.request.get('subject')
            content = self.request.get('content')

            post = Post.get_by_id(int(post_id), parent = Post.get_posts_key())
            postkey = db.Key.from_path('Post', int(post_id), parent = Post.get_posts_key())

            # if username, subject and contents are proper, delete post (post key)
            # and if current username is same as post's username
            # else render form with error
            if username and subject and content:
                if username == post.username:
                    db.delete(postkey)
                    # TODO: post.delete() is also working find the difference
                    self.redirect('/postdeleted')
                else:
                    error = "not your post to delete!"
                    self.render("permissiondenied.html", error=error, user = self.user)

class PostDeleted(BlogHandler):

    def get(self):
        self.render("deleted.html", entityname = 'Post', user = self.user)


class Like(db.Model, BlogHandler):
    '''
    Post entity in data store
    '''

    post_id = db.StringProperty(required = True)
    username = db.StringProperty(required = True)
    like = db.BooleanProperty()

    @classmethod
    def get_likes_key(cls, name = 'default'):
        '''
        define a parent group 'posts' identified by 'default' 
        useful for attaching data of all posts
        '''
        return db.Key.from_path('likes', name)

    @classmethod
    def get_like_status(cls, post_id, username = False):
        return Like.get_by_id(int(post_id), parent = Like.get_likes_key())

    @classmethod
    def get_like_by_id(cls, like_id):
        return Like.get_by_id(int(like_id), parent = Like.get_likes_key())

    @classmethod
    def get_likes(cls, post_id, username):
        post_id = str(post_id)
        username = str(username)
        likes = Like.all().filter('username = ', username).filter('post_id = ', post_id).ancestor(Like.get_likes_key())
        return likes

    @classmethod
    def get_likes_count(cls, post_id):
        post_id = str(post_id)
        likes = Like.all().filter('post_id = ', post_id).ancestor(Like.get_likes_key())
        return likes.count()

class LikePost(BlogHandler):
    '''
    Handle new posts (submission & redirect)
    '''

    def get(self, post_id):
        if self.user:
            # get request params
            username = self.user.username

            #get post
            post = Post.get_by_id(int(post_id), parent = Post.get_posts_key())

            # if username, subject and contents are proper, put on db and redirect
            # else render form with error
            if username != post.username:
                like = Like(parent = Like.get_likes_key(), post_id = post_id, username = username, like = True)
                like.put()
                self.redirect('/post/%s' % str(post_id))
            else:
                self.redirect('/post/%s' % str(post_id))

class UnlikePost(BlogHandler):
    '''
    Handle new posts (submission & redirect)
    '''

    def get(self, post_id):
        if self.user:
            # get request params
            username = self.user.username

            likes = Like.get_likes(post_id, username)

            if not likes.count():
                self.redirect('/post/%s' % str(post_id))
                return

            like = likes[0]

            if like.username == username:
                like.delete()

            self.redirect('/post/%s' % str(post_id))
            return

# define handlers
app = webapp2.WSGIApplication([ ('/', BlogFront),
                                ('/signup', Signup),
                                ('/login', Login),
                                ('/logout', Logout),
                                ('/newpost', NewPost),
                                ('/post/([0-9]+)', PostPage),
                                ('/editpost/([0-9]+)', EditPost),
                                ('/deletepost/([0-9]+)', DeletePost),
                                ('/postdeleted', PostDeleted),
                                ('/likepost/([0-9]+)', LikePost),
                                ('/unlikepost/([0-9]+)', UnlikePost)
                               ],
                              debug=True)
