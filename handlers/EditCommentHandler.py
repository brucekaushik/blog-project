from handlers import BlogHandler
from models  import Comment
from helpers import CommentHelper
from helpers import PostHelper

class EditCommentHandler(BlogHandler):
    '''
    Handle edit comments
    '''

    def get(self, comment_id, post_id):
        '''
        render edit comment form
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
                "permissiondenied.html", error=error, user=self.user)
            return
        else:
            self.render(
                'editcomment.html', user=self.user, comment=comment, post=post)
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

        # get posted values
        username = self.user.username
        newedit = self.request.get('comment')

        if username != comment.username:
            # render permission denied form
            error = "not your comment to edit!"
            self.render(
                "permissiondenied.html", error=error, user=self.user)
            return

        if username and newedit:
            # put comment on db
            comment.comment = str(newedit)
            comment.put()
            self.redirect('/post/%s' % str(post_id))
            return
        else:
            # render form with error
            error = "Comment can't be empty!"
            self.render(
                'editcomment.html',
                user=self.user,
                comment=comment,
                post=post,
                error=error
            )
            return