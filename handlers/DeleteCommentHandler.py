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
        post = PostHelper.get_post_by_id(post_id)
        comment = CommentHelper.get_comment_by_id(comment_id)

        if not post and comment:
            self.redirect('/')
            return

        if not self.user:
            self.redirect('/login')
            return

        if self.user.username != comment.username:
            error = "not your comment to edit!"
            self.render(
                "permissiondenied.html",
                error=error,
                user=self.user)
            return
        else:
            # render delete comment form
            self.render(
                "deletecomment.html",
                user=self.user,
                comment=comment,
                post=post)
            return

    def post(self, comment_id, post_id):

        post = PostHelper.get_post_by_id(post_id)
        comment = CommentHelper.get_comment_by_id(comment_id)

        if not post and comment:
            self.redirect('/')
            return

        if not self.user:
            self.redirect('/login')
            return

        if self.user.username != comment.username:
            error = "not your comment to edit!"
            self.render(
                "permissiondenied.html", error=error, user=self.user)
            return

        if comment.username == self.user.username:
            # delete comment from db
            comment.delete()
            self.redirect('/post/%s' % str(post_id))
            return
