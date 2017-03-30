from BlogHandler import BlogHandler
from helpers import PostHelper
from google.appengine.ext import db

class BlogFrontHandler(BlogHandler):
    '''
    blog front page, with recent 10 posts
    '''

    def get(self):
        '''
        get 10 recent posts from Post entity and render them using front.html
        note: doing this by using gql for practice
        '''

        # fetch posts from db
        posts = db.GqlQuery(
            "select * from Post order by created desc limit 10")

        # render front page
        self.render('front.html', posts=posts, user=self.user, post_helper=PostHelper)