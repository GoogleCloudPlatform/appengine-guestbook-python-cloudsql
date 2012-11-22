#!/usr/bin/env/python

"""Main handlers module for guestbook sample with Cloud SQL"""

__author__ = 'tmatsuo@google.com (Takashi Matsuo)'


# standard libraries
import os

# App Engine libraries
import jinja2
import webapp2
from google.appengine.api import rdbms

# App specific libraries
import settings

class GetConnection():
    """A guard class for ensuring the connection will be closed."""

    def __init__(self):
        self.conn = None

    def __enter__(self):
        self.conn = rdbms.connect(instance=settings.CLOUDSQL_INSTANCE,
                                  database=settings.DATABASE_NAME,
                                  user=settings.USER_NAME,
                                  password=settings.PASSWORD, charset='utf8')
        return self.conn

    def __exit__(self, type, value, traceback):
        self.conn.close()


jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__))))


class MainHandler(webapp2.RequestHandler):

    def get(self):
        # Viewing guestbook
        with GetConnection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT guest_name, content, created_at FROM entries'
                           ' ORDER BY created_at DESC limit 20')
            rows = cursor.fetchall()
        template_values = {'rows': rows}
        template = jinja2_env.get_template('index.html')
        self.response.out.write(template.render(template_values))


class GuestBook(webapp2.RequestHandler):

    def post(self):
        # Posting a new guestbook entry
        with GetConnection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO entries (guest_name, content) '
                           'VALUES (%s, %s)',
                           (self.request.get('guest_name'),
                            self.request.get('content')))
            conn.commit()
        self.redirect('/')


application = webapp2.WSGIApplication(
    [
        ('/', MainHandler),
        ('/sign', GuestBook),
    ],
    debug=True
)
