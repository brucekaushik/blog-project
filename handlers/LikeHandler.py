from models import Like
from models import Post
from handlers import BlogHandler
from helpers import LikeHelper
from helpers import PostHelper

class LikeHandler(BlogHandler):
    '''
    Handle like requests
    '''

    def get(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        # get post using post id
        post = PostHelper.get_post_by_id(post_id)

        if not post:
            self.redirect('/')
            return

        username = self.user.username
            
        # get user's likes for post (can be more than 1, bugs??)
        likes_of_user = LikeHelper.get_postlikes_by_username(post_id, username)

        if likes_of_user.count():
            self.redirect('/post/%s' % str(post_id))
            return

        if username != post.username:
            # build like object
            like = Like(parent=LikeHelper.get_likes_key(),
                        post_id=post_id,
                        username=username, like=True)

            # put like on db
            like.put()

        self.redirect('/post/%s' % str(post_id))
        return