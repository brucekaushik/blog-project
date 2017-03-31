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

from handlers import BlogHandler,\
    BlogFrontHandler,\
    SignupHandler,\
    LoginHandler,\
    LogoutHandler,\
    NewPostHandler,\
    ViewPostHandler,\
    EditPostHandler,\
    DeletePostHandler,\
    PostDeletedHandler,\
    LikeHandler,\
    UnlikeHandler,\
    NewCommentHandler,\
    EditCommentHandler,\
    DeleteCommentHandler
from helpers import BlogHelper,\
    LikeHelper,\
    PostHelper,\
    CommentHelper
from models import Post,\
    Like,\
    Comment


# define handlers
app = webapp2.WSGIApplication([('/', BlogFrontHandler),
                               ('/signup', SignupHandler),
                               ('/login', LoginHandler),
                               ('/logout', LogoutHandler),
                               ('/newpost', NewPostHandler),
                               ('/post/([0-9]+)', ViewPostHandler),
                               ('/editpost/([0-9]+)', EditPostHandler),
                               ('/deletepost/([0-9]+)', DeletePostHandler),
                               ('/postdeleted', PostDeletedHandler),
                               ('/likepost/([0-9]+)', LikeHandler),
                               ('/unlikepost/([0-9]+)', UnlikeHandler),
                               ('/newcomment/([0-9]+)', NewCommentHandler),
                               ('/editcomment/([0-9]+)/([0-9]+)',
                                EditCommentHandler),
                               ('/deletecomment/([0-9]+)/([0-9]+)',
                                DeleteCommentHandler)
                               ],
                              debug=True)
