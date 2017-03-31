from handlers import BlogHandler
from models import Post
from helpers import PostHelper
from google.appengine.ext import db


class DeletePostHandler(BlogHandler):

    '''
    Handle post deletions
    '''

    def get(self, post_id):
        '''
        render delete post form
        '''
        if not self.user:
            self.redirect('/login')
            return

        # get post by id
        post = PostHelper.get_post_by_id(int(post_id))

        if not post:
            self.redirect('/')
            return

        # replace <br> with new lines
        post.content = post.content.replace('<br>', '\n')

        if self.user.username != post.username:
            # render permission denied form
            error = "not your post to delete!"
            self.render(
                "permissiondenied.html", error=error, user=self.user)
            return
        else:
            # render delete post form
            self.render("deletepost.html", user=self.user, post=post)
            return

    def post(self, post_id):

        if not self.user:
            self.redirect('/login')
            return

        # get post by id
        post = PostHelper.get_post_by_id(int(post_id))

        if not post:
            self.redirect('/')
            return

        # get posted values
        username = self.user.username
        subject = self.request.get('subject')
        content = self.request.get('content')

        # get post key by id
        postkey = db.Key.from_path(
            'Post', int(post_id), parent=PostHelper.get_posts_key())

        if username and subject and content:
            if username == post.username:
                # delete post (post key) from db
                db.delete(postkey)
                # TODO: post.delete() is also working find the difference
                self.redirect('/postdeleted')
                # self.redirect('/')
                # TODO: clarify, why is this showing post on home page?
                return
            else:
                # render permission denied form
                error = "not your post to delete!"
                self.render(
                    "permissiondenied.html", error=error, user=self.user)
                return
