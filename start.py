import webapp2
import logging
import re
import jinja2
import os
from google.appengine.ext import db
import time

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'])

class Art(db.Model):
	title = db.StringProperty()
	art = db.TextProperty()

	created = db.DateTimeProperty(auto_now_add=True)




class MyHandler(webapp2.RequestHandler):
	def write(self, *writeArgs):    
		self.response.write(" : ".join(writeArgs))

	def render_str(self, template, **params):
		tplt = JINJA_ENVIRONMENT.get_template('templates/'+template)
		return tplt.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class MainPage(MyHandler):
	def render_ascii(self, title="", art="", error=""):
		arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")
		self.render("ascii.html", title=title, art=art, error=error, arts=arts)
	def get(self):
		logging.info("********** MainPage GET **********")
		error = ""
		python_dictionary = {}   # creating a new dictionary
		python_dictionary['error'] = error
		self.render_ascii()
	def post(self):
		title = self.request.get('title')
		art = self.request.get('art')
		logging.info(title)
		logging.info(art)
		if(len(title)==0 or len(art)==0):
			error="Need both a title and some artwork!"
			python_dictionary = {}   # creating a new dictionary
			python_dictionary['error'] = error
			self.render_ascii("","",error)
		else:
			artInst = Art()
			artInst.title=title
			artInst.art=art
			artInst.put()
			time.sleep(0.2)
			self.render_ascii(title, art)

class FavPage(MyHandler):
	def get(self):
		logging.info(Art.get_by_id(6333186975989760))
		self.render("fav.html", art=Art.get_by_id(6333186975989760).art)





application = webapp2.WSGIApplication([
	('/', MainPage),
	('/favorite', FavPage)
], debug=True)
