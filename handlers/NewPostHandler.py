from BlogHandler import BlogHandler
from models import Post
from helpers import PostHelper

class NewPostHandler(BlogHandler):
    '''
    Handle new posts
    '''

    def get(self):
        '''
        render new post form
        '''
        if self.user:
            self.render("newpost.html", user=self.user)
        else:
            self.redirect('/login')

    def post(self):
        if not self.user:
            self.redirect('/login')

        # get request params
        username = self.user.username
        subject = self.request.get('subject')
        content = self.request.get('content')

        if username and subject and content:
            # build post object
            p = Post(parent=PostHelper.get_posts_key(),
                     username=username, subject=subject, content=content)

            # put post in db
            p.put()

            # redirect to post page
            self.redirect('/post/%s' % str(p.key().id()))
            return
        else:
            error = "subject and content, please!"
            self.render(
                "newpost.html",
                user=self.user,
                subject=subject,
                content=content,
                error=error)
                