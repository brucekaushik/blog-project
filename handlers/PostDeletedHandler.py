from handlers import BlogHandler

class PostDeletedHandler(BlogHandler):
    '''
    post deleted form (intermediate step)
    '''

    def get(self):
        '''
        render post deleted form (for notification purpose)
        '''
        self.render("deleted.html", entityname='Post', user=self.user)