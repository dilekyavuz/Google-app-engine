import os
import secrets
import jinja2
import webapp2
import json

from google.appengine.ext import ndb
from google.appengine.api import users

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Author(ndb.Model):
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Entry(ndb.Model):
    content = ndb.StringProperty(indexed=False)
    author = ndb.StructuredProperty(Author)
    date = ndb.DateTimeProperty(auto_now_add=True)




class Main(webapp2.RequestHandler):
    def get(self):
        chat_token = secrets.token_urlsafe()

        template_values = {
            'chat_token': chat_token
        }

        template = JINJA_ENVIRONMENT.get_template('/templates/info.html')
        self.response.write(template.render(template_values))




class Chat(webapp2.RequestHandler):
    def get(self):

        chat_code = self.request.get('chat_code')
        """Using chat code as the data store key"""
        chat_datastore_key = ndb.Key('Chat',chat_code)
        entries_query = Entry.query(ancestor=chat_datastore_key).order(Entry.date)
        entries = entries_query.fetch(offset=1)
        init_url = self.request.url
        ip_adr = self.request.remote_addr


        user = users.get_current_user()
        user_url = ""

        if not user:
            user_url = users.create_login_url(self.request.uri)


        template_values = {
            'user':user,
            'user_url':user_url,
            'entries':entries,
            'chat_code':chat_code,
            'init_url':init_url

        }

        template = JINJA_ENVIRONMENT.get_template('/templates/chat.html')
        self.response.write(template.render(template_values))



    def post(self):
        chat_code = self.request.get('chat_code')
        entry_content = self.request.get('entry')
        ip_adr = self.request.remote_addr
        user = users.get_current_user()



        chat_datastore_key = ndb.Key('Chat',chat_code)

        entry = Entry(parent=chat_datastore_key)
        entry.content = entry_content

        if user:
            entry.author = Author(email=user.email(),
                                  identity=user.user_id())




        entry.put()
        self.redirect("/chat?chat_code="+chat_code)



app = webapp2.WSGIApplication([
    ('/', Main),
    ('/chat',Chat)
], debug=True)



