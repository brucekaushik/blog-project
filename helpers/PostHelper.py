from google.appengine.ext import db
from models import Post
import os
import jinja2
import BlogHelper
import LikeHelper
import CommentHelper

# build path to templates directory
template_dir = os.path.join(os.path.dirname(__file__), "../templates")
# initialize jinja environment
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

def render_post_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)

def get_posts_key(name='default'):
    '''
    define a parent group 'posts' identified by 'default'
    useful for attaching data of all posts
    '''
    return db.Key.from_path('posts', name)


def get_post_by_id(post_id):
    '''
    get post object by post id
    '''
    return Post.get_by_id(int(post_id), parent=get_posts_key())

def render_post(post_id, session_user=False, show_comments=False):
	'''
	render blog post (html string) using post id
	'''

	# get post
	post = get_post_by_id(post_id)

	if post:
		
		if session_user:
		    # get likes by post id and username
		    likes = LikeHelper.get_postlikes_by_username(
		        post_id, session_user.username)

		    # get latest like id (in case post got liked by the same user
		    # multiple times)
		    if likes.count():
		        like_id = likes[0].key().id()
		    else:
		        like_id = 0
		else:
		    like_id = 0

		# get comments for post
		comments = CommentHelper.get_comments_for_post(post_id)

		# get likes count for post
		likes_count = LikeHelper.get_likes_count_for_post(post_id)

		# replace newlines with <br>
		post._render_text = post.content.replace('\n', '<br>')

		# render html string
		return render_post_str(
		    "post.html",
		    p=post,
		    like_id=like_id,
		    likes_count=likes_count,
		    show_comments=show_comments,
		    comments=comments
		)
	else:
		# already being checked in controller
		# this is for safety!
		return "Post Not Found!"



