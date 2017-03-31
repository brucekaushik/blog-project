from BlogHandler import BlogHandler
from helpers import BlogHelper
from helpers import UserHelper
from models import User


class SignupHandler(BlogHandler):
    '''
    handle signups here
    '''

    def get(self):
        '''
        render signup page
        '''
        self.render("signup-form.html", user=self.user)

    def post(self):
        # fetch posted values
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        # build params dictionary to pass to form
        params = dict(username=username,
                      email=email)

        # validate
        if not BlogHelper.validate_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not BlogHelper.validate_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True

        elif password != verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not BlogHelper.validate_email(email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', user=self.user, **params)
        else:
            # register user (create object)
            user = self.register(username, password, email)

            # check if user exists
            user_check = UserHelper.get_user_by_name(user.username)

            # if user exists,
            # render form with error
            # else, put in db
            if user_check:
                params['error_username'] = ("User already exists! " +
                                            "Please enter a unique username.")
                self.render('signup-form.html', user=self.user, **params)
            else:
                user.put()
                self.login(user)
                self.redirect('/')
