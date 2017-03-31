from models import Like
from models import Post
from handlers import BlogHandler
from helpers import LikeHelper
from helpers import PostHelper


class UnlikeHandler(BlogHandler):
    '''
    Handle unlike requests
    '''

    def get(self, post_id):
        if not self.user:
            self.redirect('/login')

        # get post using post id
        post = PostHelper.get_post_by_id(post_id)

        if not post:
            self.redirect('/')
            return

        username = self.user.username

        # get user's likes for post (can be more than 1, bugs??)
        likes_of_user = LikeHelper.get_postlikes_by_username(post_id, username)

        if not likes_of_user.count():
            self.redirect('/post/%s' % str(post_id))
            return

        # get first like object
        # (in case of multiple, due to bugs?)
        like = likes_of_user[0]

        if like.username == username:
            # delete like from db
            like.delete()

        self.redirect('/post/%s' % str(post_id))
        return
