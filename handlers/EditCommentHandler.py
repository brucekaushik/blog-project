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

        if self.user:
            c = CommentHelper.get_comment_by_id(comment_id)
            p = PostHelper.get_post_by_id(post_id)

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
            c = CommentHelper.get_comment_by_id(comment_id)

            # get post by id
            p = PostHelper.get_post_by_id(post_id)

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