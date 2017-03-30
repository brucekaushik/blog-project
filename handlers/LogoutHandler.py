from handlers import BlogHandler

class LogoutHandler(BlogHandler):
    '''
    handle logout
    '''
    def get(self):
        self.logout()
        self.redirect('/')