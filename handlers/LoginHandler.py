from handlers import BlogHandler
from helpers import BlogHelper, UserHelper
from models import User


class LoginHandler(BlogHandler):

    '''
    handle logins
    '''

    def get(self):
        self.render('login-form.html', user=self.user)

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')

        # build params dictionary to pass to form
        params = dict(username=username,
                      password=password)

        # validate
        # render form with error if validation fails
        if not BlogHelper.validate_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True
        if not BlogHelper.validate_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        if have_error:
            self.render('login-form.html', **params)
        else:
            # log the user in
            user = UserHelper.login(username, password)
            if user:
                self.login(user)
                self.redirect('/')
            else:
                params['error_login_fail'] = "Invalid username or password!"
                self.render('login-form.html', **params)
