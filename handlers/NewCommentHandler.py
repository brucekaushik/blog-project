from models import Comment
from models import Post
from handlers import BlogHandler
from helpers import PostHelper
from helpers import CommentHelper

class NewCommentHandler(BlogHandler):

    '''
    Handle new comments
    '''

    def get(self, post_id):
        '''
        render new comment form
        '''
        if self.user:
            post = Post.get_by_id(int(post_id), parent=PostHelper.get_posts_key())
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
            post = Post.get_by_id(int(post_id), parent=PostHelper.get_posts_key())

            if username and post_id and comment:
                # build comment object
                c = Comment(
                    parent=CommentHelper.get_comments_key(),
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