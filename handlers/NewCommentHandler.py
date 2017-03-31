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
        post = PostHelper.get_post_by_id(post_id)

        if not post:
            self.redirect('/')
            return

        if not self.user:
            self.redirect('/login')
            return

        self.render("newcomment.html", user=self.user, post=post)
        return

    def post(self, post_id):

        post = PostHelper.get_post_by_id(post_id)

        if not post:
            self.redirect('/')
            return

        if not self.user:
            self.redirect('/login')
            return

        # get posted values
        username = self.user.username
        comment = self.request.get('comment')

        if username and comment:
            # build comment object
            c = Comment(
                parent=CommentHelper.get_comments_key(),
                username=username, post_id=post_id,
                comment=comment
            )
            # put comment on db
            c.put()

            self.redirect('/post/%s' % str(post_id))
            return
        else:
            # render form with error
            error = "Comment can't be empty!"
            self.render(
                "newcomment.html", user=self.user, post=post, error=error)
            return