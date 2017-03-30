from handlers import BlogHandler
from models import Comment
from helpers import CommentHelper
from helpers import PostHelper

class DeleteCommentHandler(BlogHandler):
    '''
    Handle delete comment
    '''

    def get(self, comment_id, post_id):
        '''
        render delete comment form
        '''
        if self.user:
            # get comment by id
            c = CommentHelper.get_comment_by_id(comment_id)

            # get post by id
            p = PostHelper.get_post_by_id(post_id)

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
            c = CommentHelper.get_comment_by_id(comment_id)

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