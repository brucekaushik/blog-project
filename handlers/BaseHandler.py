# how do i import webapp2 here?
# should'nt it be available already??

import os
import jinja2
import webapp2

# build path to templates directory
template_dir = os.path.join(os.path.dirname(__file__), "../templates")
# initialize jinja environment
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class BaseHandler(webapp2.RequestHandler):

    '''
    inherit from this handler to access commonly used methods
    '''

    def write(self, *a, **kw):
        '''
        shorcut to using self.response.out.write
        '''
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        '''
        return html output to render, as a string
        '''
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        '''
        render html
        '''
        self.response.out.write(self.render_str(template, **kw))
