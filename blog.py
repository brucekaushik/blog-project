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
template_dir = os.path.join(os.path.dirname(__file__), "templates")
# initialize jinja environment
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

# define a secret key
SECRET = 'my secret, which is not so secret'


class BaseHandler(webapp2.RequestHandler):
    '''
    inherit from this handler to access commonly used methods
    '''

    def write(self, *a, **kw):
        '''
        shorcut to using self.response.out.write
        '''
        self.response.out.write(*a, **kw)

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
        self.user = user_id and User.get_user_by_id(int(user_id))

    def blog_key(self, name='default'):
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

    def set_cookie(self, cookie_name, cookie_val):
        '''
        set cookie cookie name and value
        '''

        # secure cookie value
        cookie_val = BlogHandler.secure_cookie_val(cookie_val)

        # set cookie by adding a http header
        self.response.headers.add_header(
            'Set-Cookie', '%s=%s; Path=/' % (cookie_name, cookie_val))

    def get_cookie(self, cookie_name):
        '''
        get cookie value by using cookie name
        '''
        cookie_val = self.request.cookies.get(cookie_name)
        return cookie_val and BlogHandler.verify_secure_cookie_val(cookie_val)

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
        password_hash = BlogHandler.hash_str(password)

        # create and return user (this does not update database)
        return User(parent=User.get_users_key(),
                    username=username,
                    password_hash=password_hash,
                    email=email)

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
        email_regex = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
        return not email or email_regex.match(email)

    @classmethod
    def hash_str(cls, string_to_hash):
        '''
        hash string by using hmac & secret
        '''
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
        note: doing this by using gql for practice
        '''

        # fetch posts from db
        posts = db.GqlQuery(
            "select * from Post order by created desc limit 10")

        # render front page
        self.render('front.html', posts=posts, user=self.user)


class Signup(BlogHandler):
    '''
    handle signups here
    '''

    def get(self):
        '''
        render signup page
        '''
        self.render("signup-form.html", user=self.user)

    def post(self):
        # fetch posted values
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        # build params dictionary to pass to form
        params = dict(username=username,
                      email=email)

        # validate
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
            self.render('signup-form.html', user=self.user, **params)
        else:
            # register user (create object)
            user = self.register(username, password, email)

            # check if user exists
            user_check = User.get_user_by_name(user.username)

            # if user exists,
            # render form with error
            # else, put in db
            if user_check:
                params['error_username'] = ("User already exists! " +
                                            "Please enter a unique username.")
                self.render('signup-form.html', user=self.user, **params)
            else:
                user.put()
                self.login(user)
                self.redirect('/')


class User(db.Model, BlogHandler):
    '''
    User entity
    '''

    username = db.StringProperty(required=True)
    password_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def get_users_key(cls, name='default'):
        '''
        define a parent group 'users' identified by 'default',
        useful for attaching data of all users
        '''
        return db.Key.from_path('users', name)

    @classmethod
    def get_user_by_id(cls, user_id):
        '''
        get user object by user id
        '''
        return User.get_by_id(user_id, parent=User.get_users_key())
        # note: get_by_id is data store build in method

    @classmethod
    def get_user_by_name(cls, username):
        '''
        get user object by username name
        '''
        return User.all().filter('username = ', username).get()

    @classmethod
    def validate_db_password(cls, username, password, password_hash):
        '''
        validate password from db with password hash
        '''
        password = BlogHandler.hash_str(password)
        return password == password_hash

    @classmethod
    def login(cls, username, password):
        '''
        return user object for logging in
        '''
        # get user by username
        user = cls.get_user_by_name(username)

        # validate password if user exists
        # return user if validation is successful
        if user and cls.validate_db_password(
                                            username,
                                            password,
                                            user.password_hash
                                            ):
            return user


class Login(BlogHandler):
    '''
    handle logins
    '''

    def get(self):
        self.render('login-form.html', user=self.user)

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')

        # validate
        # render form with error if validation fails
        if not BlogHandler.validate_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True
        if not BlogHandler.validate_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        if have_error:
            self.render('login-form.html', **params)
        else:
            # log the user in
            user = User.login(username, password)
            self.login(user)
            self.redirect('/')


class Logout(BlogHandler):
    '''
    handle logout
    '''
    def get(self):
        self.logout()
        self.redirect('/')


class Post(db.Model, BlogHandler):
    '''
    Post entity
    '''

    username = db.StringProperty(required=True)
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now_add=True)

    def render(self, session_user=False, show_comments=False):
        '''
        render blog post
        '''
        if session_user:
            # get likes by post id and username
            likes = Like.get_postlikes_by_username(
                self.key().id(), session_user.username)

            # get latest like id (in case post got liked by the same user
            # multiple times)
            if likes.count():
                like_id = likes[0].key().id()
            else:
                like_id = 0
        else:
            like_id = 0

        # get comments for post
        comments = Comment.get_comments_for_post(self.key().id())

        # get likes count for post
        likes_count = Like.get_likes_count_for_post(self.key().id())

        # replace newlines with <br>
        self._render_text = self.content.replace('\n', '<br>')

        # render html string
        return self.render_str(
                                "post.html",
                                p=self,
                                like_id=like_id,
                                likes_count=likes_count,
                                show_comments=show_comments,
                                comments=comments
                                )

    @classmethod
    def get_posts_key(cls, name='default'):
        '''
        define a parent group 'posts' identified by 'default'
        useful for attaching data of all posts
        '''
        return db.Key.from_path('posts', name)

    @classmethod
    def get_post_by_id(cls, post_id):
        '''
        get post object by post id
        '''
        return Post.get_by_id(int(post_id), parent=Post.get_posts_key())


class NewPost(BlogHandler):
    '''
    Handle new posts
    '''

    def get(self):
        '''
        render new post form
        '''
        if self.user:
            self.render("newpost.html", user=self.user)
        else:
            self.redirect('/login')

    def post(self):
        if self.user:
            # get request params
            username = self.user.username
            subject = self.request.get('subject')
            content = self.request.get('content')

            if username and subject and content:
                # build post object
                p = Post(parent=Post.get_posts_key(),
                         username=username, subject=subject, content=content)

                # put post in db
                p.put()

                # redirect to post page
                self.redirect('/post/%s' % str(p.key().id()))
            else:
                # render form with error
                error = "subject and content, please!"
                self.render(
                            "newpost.html",
                            user=self.user,
                            subject=subject,
                            content=content,
                            error=error)


class PostPage(BlogHandler):
    '''
    Handle Post Page (permalink)
    '''

    def get(self, post_id):
        '''
        get post from database and render it using template
        '''

        p = Post.get_post_by_id(post_id)

        # show 404 if post is not available
        if not p:
            self.error(404)
            self.write('Error! Post Not Found')
            return

        if not self.user:
            self.user = False

        # render post using permalink template
        # note: post will have a render method (see definition)
        # notice: render method will also be availble in jinja
        self.render("permalink.html", post=p, user=self.user)


class EditPost(BlogHandler):
    '''
    Handle edit posts
    '''

    def get(self, post_id):
        '''
        render edit post form
        '''
        if self.user:
            # get post by id
            post = Post.get_by_id(int(post_id), parent=Post.get_posts_key())

            # replace <br> in post content with new lines
            post.content = post.content.replace('<br>', '\n')

            if self.user.username != post.username:
                # render permission denied form
                error = "not your post to edit!"
                self.render(
                    "permissiondenied.html", error=error, user=self.user)
                return

            # render edit post form
            self.render("editpost.html", user=self.user, post=post)
        else:
            self.redirect('/login')

    def post(self, post_id):
        if self.user:
            # get posted values
            username = self.user.username
            subject = self.request.get('subject')
            content = self.request.get('content')

            # get post by id
            post = Post.get_by_id(
                                int(post_id),
                                parent=Post.get_posts_key())

            if username and subject and content:
                # replace subject with new subject
                post.subject = subject

                # replace content with new content
                # replace new lines with <br>
                post.content = content.replace('\n', '<br>')

                if username == post.username:
                    # put edited post on db
                    post.put()

                    # redirect to post page
                    self.redirect('/post/%s' % str(post_id))
                else:
                    # render permission denied form
                    error = "not your post to edit!"
                    self.render("permissiondenied.html",
                                error=error,
                                user=self.user)
            else:
                # render form with error
                error = "subject and content, please!"
                self.render(
                            "editpost.html",
                            post = post,
                            user=self.user,
                            subject=subject,
                            content=content,
                            error=error)
        else:
            self.redirect('/login')


class DeletePost(BlogHandler):
    '''
    Handle post deletions
    '''

    def get(self, post_id):
        '''
        render delete post form
        '''
        if self.user:
            # get post by id
            post = Post.get_by_id(int(post_id), parent=Post.get_posts_key())

            # replace <br> with new lines
            post.content = post.content.replace('<br>', '\n')

            if self.user.username != post.username:
                # render permission denied form
                error = "not your post to delete!"
                self.render(
                    "permissiondenied.html", error=error, user=self.user)
                return

            # render delete post form
            self.render("deletepost.html", user=self.user, post=post)
        else:
            self.redirect('/login')

    def post(self, post_id):
        if self.user:
            # get posted values
            username = self.user.username
            subject = self.request.get('subject')
            content = self.request.get('content')

            # get post by id
            post = Post.get_by_id(int(post_id), parent=Post.get_posts_key())

            # get post key by id
            postkey = db.Key.from_path(
                'Post', int(post_id), parent=Post.get_posts_key())

            if username and subject and content:
                if username == post.username:
                    # delete post (post key) from db
                    db.delete(postkey)
                    # TODO: post.delete() is also working find the difference
                    self.redirect('/postdeleted')
                else:
                    # render permission denied form
                    error = "not your post to delete!"
                    self.render(
                        "permissiondenied.html", error=error, user=self.user)
        else:
            self.redirect('/login')


class PostDeleted(BlogHandler):
    '''
    post deleted form (intermediate step)
    '''

    def get(self):
        '''
        render post deleted form (for notification purpose)
        '''
        self.render("deleted.html", entityname='Post', user=self.user)


class Like(db.Model, BlogHandler):
    '''
    Post entity
    '''

    post_id = db.StringProperty(required=True)
    username = db.StringProperty(required=True)
    like = db.BooleanProperty()

    @classmethod
    def get_likes_key(cls, name='default'):
        '''
        define a parent group 'likes' identified by 'default'
        useful for attaching data of all likes
        '''
        return db.Key.from_path('likes', name)

    @classmethod
    def get_like_by_id(cls, like_id):
        '''
        get like object by like id
        '''
        return Like.get_by_id(int(like_id), parent=Like.get_likes_key())

    @classmethod
    def get_postlikes_by_username(cls, post_id, username):
        '''
        get likes of post by username and post_id
        '''
        post_id = str(post_id)
        username = str(username)
        likes = Like.all().filter('username = ', username).filter(
            'post_id = ', post_id).ancestor(Like.get_likes_key())
        return likes

    @classmethod
    def get_likes_count_for_post(cls, post_id):
        '''
        get likes count for a post
        '''
        post_id = str(post_id)
        likes = Like.all().filter(
            'post_id = ', post_id).ancestor(Like.get_likes_key())
        return likes.count()


class LikePost(BlogHandler):
    '''
    Handle like requests
    '''

    def get(self, post_id):
        if self.user:
            username = self.user.username

            # get post using post id
            post = Post.get_by_id(int(post_id), parent=Post.get_posts_key())

            if username != post.username:
                # build like object
                like = Like(parent=Like.get_likes_key(),
                            post_id=post_id,
                            username=username, like=True)

                # put like on db
                like.put()

                self.redirect('/post/%s' % str(post_id))
            else:
                self.redirect('/post/%s' % str(post_id))
        else:
            self.redirect('/login')


class UnlikePost(BlogHandler):

    '''
    Handle unlike requests
    '''

    def get(self, post_id):
        if self.user:
            username = self.user.username

            # get likes for the post and user
            likes = Like.get_postlikes_by_username(post_id, username)

            if not likes.count():
                self.redirect('/post/%s' % str(post_id))
                return

            # get first like object
            # (in case of multiple, due to bugs?)
            like = likes[0]

            if like.username == username:
                # delete like from db
                like.delete()

            self.redirect('/post/%s' % str(post_id))
            return
        else:
            self.redirect('/login')


class Comment(db.Model, BlogHandler):
    '''
    Comment entity
    '''

    post_id = db.StringProperty(required=True)
    username = db.StringProperty(required=True)
    comment = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def get_comments_key(cls, name='default'):
        '''
        define a parent group 'comments' identified by 'default'
        useful for attaching data of all comments
        '''
        return db.Key.from_path('comments', name)

    @classmethod
    def get_comments_for_post(cls, post_id):
        '''
        get all comments for a post
        '''
        post_id = str(post_id)
        comments = Comment.all().filter(
            'post_id = ', post_id).ancestor(Comment.get_comments_key())
        return comments

    @classmethod
    def get_comment_by_id(cls, comment_id):
        '''
        get comment object by comment id
        '''
        return Comment.get_by_id(
                                int(comment_id),
                                parent=Comment.get_comments_key()
                                )


class NewComment(BlogHandler):
    '''
    Handle new comments
    '''

    def get(self, post_id):
        '''
        render new comment form
        '''
        if self.user:
            post = Post.get_by_id(int(post_id), parent=Post.get_posts_key())
            self.render("newcomment.html", user=self.user, post=post)
        else:
            self.redirect('/login')

    def post(self, post_id):
        if self.user:
            # get posted values
            username = self.user.username
            comment = self.request.get('comment')
            post_id = self.request.get('post_id')

            # get post by id
            post = Post.get_by_id(int(post_id), parent=Post.get_posts_key())

            if username and post_id and comment:
                # build comment object
                c = Comment(
                            parent=Comment.get_comments_key(),
                            username=username, post_id=post_id,
                            comment=comment
                            )

                # put comment on db
                c.put()
                self.redirect('/post/%s' % str(post_id))
            else:
                # render form with error
                error = "Comment can't be empty!"
                self.render(
                    "newcomment.html", user=self.user, post=post, error=error)
        else:
            self.redirect('/login')


class EditComment(BlogHandler):
    '''
    Handle edit comments
    '''

    def get(self, comment_id, post_id):
        '''
        render edit comment form
        '''
        if self.user:
            c = Comment.get_comment_by_id(comment_id)
            p = Post.get_post_by_id(post_id)

            if self.user.username != c.username:
                error = "not your comment to edit!"
                self.render(
                    "permissiondenied.html", error=error, user=self.user)
            else:
                self.render(
                    'editcomment.html', user=self.user, comment=c, post=p)
        else:
            self.redirect('/login')

    def post(self, comment_id, post_id):
        if self.user:
            # get posted values
            username = self.user.username
            comment = self.request.get('comment')
            comment_id = self.request.get('comment_id')

            # get comment by id
            c = Comment.get_comment_by_id(comment_id)

            # get post by id
            p = Post.get_post_by_id(post_id)

            if self.user.username != c.username:
                # render permission denied form
                error = "not your comment to edit!"
                self.render(
                    "permissiondenied.html", error=error, user=self.user)
                return

            if username and post_id and comment:
                # put comment on db
                c.comment = str(comment)
                c.put()
                self.redirect('/post/%s' % str(post_id))
            else:
                # render form with error
                error = "Comment can't be empty!"
                self.render(
                            'editcomment.html',
                            user=self.user,
                            comment=c,
                            post=p,
                            error=error
                            )
        else:
            self.redirect('/login')


class DeleteComment(BlogHandler):
    '''
    Handle delete comment
    '''

    def get(self, comment_id, post_id):
        '''
        render delete comment form
        '''
        if self.user:
            # get comment by id
            c = Comment.get_comment_by_id(comment_id)

            # get post by id
            p = Post.get_post_by_id(post_id)

            if self.user.username != c.username:
                # render permission denied form
                error = "not your comment to delete!"
                self.render(
                    "permissiondenied.html", error=error, user=self.user)
                return

            # render delete comment form
            self.render(
                "deletecomment.html", user=self.user, comment=c, post=p)
        else:
            self.redirect('/login')

    def post(self, comment_id, post_id):
        if self.user:
            # get comment by id
            c = Comment.get_comment_by_id(comment_id)

            if c.username == self.user.username:
                # delete comment from db
                c.delete()
                self.redirect('/post/%s' % str(post_id))
                return
            else:
                # render permission denied form
                error = "not your comment to delete!"
                self.render(
                    "permissiondenied.html", error=error, user=self.user)
                return
        else:
            self.redirect('/login')

# define handlers
app = webapp2.WSGIApplication([('/', BlogFront),
                               ('/signup', Signup),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/newpost', NewPost),
                               ('/post/([0-9]+)', PostPage),
                               ('/editpost/([0-9]+)', EditPost),
                               ('/deletepost/([0-9]+)', DeletePost),
                               ('/postdeleted', PostDeleted),
                               ('/likepost/([0-9]+)', LikePost),
                               ('/unlikepost/([0-9]+)', UnlikePost),
                               ('/newcomment/([0-9]+)', NewComment),
                               ('/editcomment/([0-9]+)/([0-9]+)',
                                EditComment),
                               ('/deletecomment/([0-9]+)/([0-9]+)',
                                DeleteComment)
                               ],
                              debug=True)
