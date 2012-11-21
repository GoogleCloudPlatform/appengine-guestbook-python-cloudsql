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

def get_connection():
    return rdbms.connect(instance=settings.CLOUDSQL_INSTANCE,
                         database=settings.DATABASE_NAME,
                         user=settings.USER_NAME,
                         password=settings.PASSWORD, charset='utf8')


jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__))))


class MainHandler(webapp2.RequestHandler):

    def get(self):
        # Viewing guestbook
        with get_connection() as conn:
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
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO entries (guest_name, content) '
                       'VALUES (%s, %s)',
                       (self.request.get('guest_name'),
                        self.request.get('content')))
        conn.commit()
        conn.close()
        self.redirect('/')


application = webapp2.WSGIApplication(
    [
        ('/', MainHandler),
        ('/sign', GuestBook),
    ],
    debug=True
)
