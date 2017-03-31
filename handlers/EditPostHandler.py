from handlers import BlogHandler
from models import Post
from helpers import PostHelper


class EditPostHandler(BlogHandler):

    '''
    Handle edit posts
    '''

    def get(self, post_id):
        '''
        render edit post form
        '''
        if not self.user:
            self.redirect('/login')
            return

        # get post by id
        post = PostHelper.get_post_by_id(int(post_id))

        if not post:
            self.redirect('/')
            return

        # replace <br> in post content with new lines
        post.content = post.content.replace('<br>', '\n')

        if self.user.username != post.username:
            # render permission denied form
            error = "not your post to edit!"
            self.render(
                "permissiondenied.html", error=error, user=self.user)
            return

        # render edit post form
        self.render("editpost.html", user=self.user, post=post)
        return

    def post(self, post_id):
        if not self.user:
            self.redirect('/login')

        # get post by id
        post = PostHelper.get_post_by_id(int(post_id))

        if not post:
            self.redirect('/')
            return

        # get posted values
        username = self.user.username
        subject = self.request.get('subject')
        content = self.request.get('content')

        if username and subject and content:
            # replace subject with new subject
            post.subject = subject

            # replace content with new content
            # replace new lines with <br>
            post.content = content.replace('\n', '<br>')

            if username == post.username:
                # put edited post on db
                post.put()

                # redirect to post page
                self.redirect('/post/%s' % str(post_id))
                return
            else:
                # render permission denied form
                error = "not your post to edit!"
                self.render("permissiondenied.html",
                            error=error,
                            user=self.user)
                return
        else:
            # render form with error
            error = "subject and content, please!"
            self.render(
                "editpost.html",
                post=post,
                user=self.user,
                subject=subject,
                content=content,
                error=error)
            return
