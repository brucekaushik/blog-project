from handlers import BlogHandler
from helpers import PostHelper


class ViewPostHandler(BlogHandler):
    '''
    Handle Post Page (permalink)
    '''

    def get(self, post_id):
        '''
        get post from database and render it using template
        '''

        post = PostHelper.get_post_by_id(post_id)

        # show 404 if post is not available
        if not post:
            self.error(404)
            self.write('Error! Post Not Found')
            return

        if not self.user:
            self.user = False

        # render post using permalink template
        # note: post will have a render method (see definition)
        # notice: render method will also be availble in jinja
        self.render("permalink.html",
                    post=post,
                    user=self.user,
                    post_helper=PostHelper)
