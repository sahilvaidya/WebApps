import webapp2
import logging
import re
import jinja2
import os
from google.appengine.ext import db
import time
from random import randint
import cgi
import hashlib
import hmac
import urllib2
from xml.dom import minidom
import json
from datetime import datetime, timedelta
from google.appengine.api import memcache
def get_coords(ip):
	page = urllib2.urlopen("http://freegeoip.net/xml/" + ip)
	dom = minidom.parseString(page.read())
	
	countryCode = dom.getElementsByTagName("CountryCode")[0].childNodes
	if countryCode.length > 0:
		latitude = dom.getElementsByTagName("Latitude")[0].childNodes[0].nodeValue
		longitude = dom.getElementsByTagName("Longitude")[0].childNodes[0].nodeValue
		return db.GeoPt(latitude, longitude)
	return None


	

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'])

userre = re.compile(r"^([a-z0-9_\-A-Z]{3,20})");
passre = re.compile(r"^(.{3,20})");
emailre= re.compile(r"^(.{1,20}@.{1,20}\..{1,20})")

def hash_str(s):
	return hmac.new("imsosecret",str(s)).hexdigest()

def make_secure_val(s):
	return str(str(s)+"|"+hash_str(s))

def check_secure_val(h):
	s,ha=h.split('|')
	has=hash_str(s)
	if ha==has:
		return s
	else:
		return None


def make_salt():
	h=""
	while len(h)<25:
		h=h+str(randint(0, 9))
	return h

def make_pw_hash(name, pw, salt=None):
	if not salt:
		salt=make_salt()
	hashs = hash_str(name+""+pw+""+salt)
	rstring=hashs+"|"+salt
	return rstring

def valid_pw(name,pw,h):
	code,salt = h.split('|')
	check=make_pw_hash(name,pw,salt)
	logging.info("check:"+check)
	if h==check:
		return True
	return False


def validate():
	userhash = self.request.cookies.get('userid', None)
	i,j = userhash.split('|')
	if userhash:
		if check_secure_val(userhash):
			return Users.get_by_id(i).username
	self.redirect('/blog/signup')

def mc_set(key, val):
	mcTime=datetime.utcnow()
	memcache.set(key,(val, mcTime))
	return None

def mc_get(key):
	if memcache.get(key):
		val,mcTime = memcache.get(key)
		age=(datetime.utcnow() - mcTime).total_seconds()
		return (val,age)
	else:
		return (None,0)

def top_post(update):
	post,time=mc_get('hit')
	if post == None or update:
		logging.info(">>> DATABASE ACCESS <<<")
		posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC Limit 10" )
		mc_set('hit',posts)
		return mc_get('hit')
	else:
		logging.info(">>> CACHE HIT <<<")
		return mc_get('hit')


def age_str(age):
	s = 'DB accessed %s seconds ago'
	age = int(age)
	if age == 1:
		s = s.replace('seconds', 'second')
	return s % age

class Post(db.Model):
	subject = db.StringProperty()
	blog = db.TextProperty()
	created = db.DateTimeProperty(auto_now_add=True)
	coords  = db.GeoPtProperty()
	def as_dict(self):
		time_fmt = '%c'
		d = {'subject' : self.subject, 'content' : self.blog, 'created' : self.created.strftime(time_fmt)}
		return d

class Users(db.Model):
	username=db.StringProperty()
	passhash=db.StringProperty()
	email=db.StringProperty()






class MyHandler(webapp2.RequestHandler):
	def write(self, *writeArgs):    
		self.response.write(" : ".join(writeArgs))

	def render_str(self, template, **params):
		tplt = JINJA_ENVIRONMENT.get_template('templates/'+template)
		return tplt.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

	def render_json(self, d):
		json_txt = json.dumps(d)
		self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
		self.write(json_txt)


class MainPage(MyHandler):
	def get(self, subject="", blog="", error="", update=""):
		userhash=self.request.cookies.get('userid','DNE')
		logging.info(userhash)
		template_values={}
		if not userhash=='DNE' and not userhash=='' and check_secure_val(userhash):
			loggedUser = Users.get_by_id(int(check_secure_val(userhash)))
			posts,mcTime = top_post(update)
			mcTime=age_str(mcTime)
			if self.request.url.endswith('.json'):
				self.render_json([post.as_dict() for post in posts])
			else:
				self.render("posts.html", posts=posts, username=loggedUser.username, age=mcTime)
		else:
			posts,mcTime = top_post(update)
			if self.request.url.endswith('.json'):
				self.render_json([post.as_dict() for post in posts])
			else:
				self.render("posts.html", posts=posts, age=mcTime)

class EntryPage(MyHandler):
	def get(self, product_id):
		userhash=self.request.cookies.get('userid','DNE')
		if userhash=='DNE' or userhash=='' or not check_secure_val(userhash):
			self.redirect('/blog')
		else:
			newprod,mcTime=mc_get(product_id)
			if newprod==None:
				mc_set(product_id,Post.get_by_id(int(product_id)))
			newprod,mcTime=mc_get(product_id)
			mcTime=age_str(mcTime)
			loggedUser = Users.get_by_id(int(check_secure_val(userhash)))
			if self.request.url.endswith('.json'):
				self.render_json([newprod.as_dict()])
			else:
				self.render("npst.html", post=newprod, username=loggedUser.username, age=mcTime)
class NewPage(MyHandler):
	def get(self):
		userhash=self.request.cookies.get('userid','DNE')
		if userhash=='DNE' or userhash=='' or not check_secure_val(userhash):
			self.redirect('/blog')
		else:
			loggedUser = Users.get_by_id(int(check_secure_val(userhash)))
			self.render("newpost.html", username=loggedUser.username)
	def post(self):
		error=""
		subject = self.request.get('subject')
		blog = self.request.get('content')
		ip = self.request.get('location')
		userhash=self.request.cookies.get('userid','DNE')
		if(len(subject)==0 or len(blog)==0):
			error="Need both a subject and text!"
			if userhash=='DNE' or userhash=='' or not check_secure_val(userhash):
				self.redirect('/blog')
			loggedUser = Users.get_by_id(int(check_secure_val(userhash)))
			self.render("newpost.html",error=error)
		else:
			postInst = Post()
			postInst.coords = get_coords(ip)
			postInst.subject=subject
			postInst.blog=blog
			postInst.put()
			time.sleep(0.2)
			top_post(update=True)
			self.redirect("/blog/"+str(postInst.key().id()))

class SignupPage(MyHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		template_values = {"username": "","password": "", "verify":"", "email": "", "eusername":"", "everify":"", "epassword":"","eemail":""}
		template = JINJA_ENVIRONMENT.get_template('templates/index.htm')
		self.response.write(template.render(template_values))
	def post(self):
		success=True;
		eu="";
		ep="";
		ee="";
		ev="";
		User=self.request.get("username");
		Pass=self.request.get("password");
		Veri=self.request.get("verify");
		Emai=self.request.get("email");
		if(not(re.search(userre,User))):
			eu="Incorrect Username";
			success=False;
		if(not(re.search(passre,Pass))):
			ep="Incorrect Password";
			success=False;
		if(not(Pass==Veri)):
			ev="The password does not match";
			success=False;
		if(len(Emai)>0 and not(re.search(emailre,Emai))):
			ee="That is not a valid password"
			success=False;
		

		if success and not db.GqlQuery("SELECT * FROM Users WHERE username = '%s'" % User).count():
			userInst=Users()
			userInst.username=User
			userInst.passhash=make_pw_hash(User,Pass)
			userInst.put()
			userInstId=str(userInst.key().id())
			self.response.headers.add_header('Set-Cookie', 'userid=%s; Path=/; Max-Age=86400' % make_secure_val(userInstId))


			self.redirect("/blog/success")
		elif db.GqlQuery("SELECT * FROM Users WHERE username = '%s'" % User).count():
			logging.info(User)
			eu="This username has been taken"
			template_values={"username": User,"password": "", "verify":"", "email": Emai, "eusername":eu, "everify":ev, "epassword":ep,"eemail":ee}
			template = JINJA_ENVIRONMENT.get_template('templates/index.htm')
			self.response.write(template.render(template_values))
		else:
			template_values={"username": User,"password": "", "verify":"", "email": Emai, "eusername":eu, "everify":ev, "epassword":ep,"eemail":ee}
			template = JINJA_ENVIRONMENT.get_template('templates/index.htm')
			self.response.write(template.render(template_values))


class WelcomePage(MyHandler):
	def get(self):
		userhash=self.request.cookies.get('userid','DNE')
		if not userhash=='DNE' and check_secure_val(userhash):
			loggedUser = Users.get_by_id(int(check_secure_val(userhash)))
			template_values = {"name": loggedUser.username, "username": loggedUser.username}
			template = JINJA_ENVIRONMENT.get_template('templates/success.htm')
			self.write(template.render(template_values))
		else:
			self.redirect("/blog/signup")


class LoginPage(MyHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		self.render('login.htm')
		
	def post(self):
		success=True;
		eu="";
		ep="";
		User=self.request.get("username");
		Pass=self.request.get("password");
		if(not(re.search(userre,User))):
			eu="Incorrect Username";
			success=False;
		if(not(re.search(passre,Pass))):
			ep="Incorrect Password";
			success=False;
		if not success:
			template_values = {"username": User,"password": "", "eusername":eu, "epassword":ep}
			template = JINJA_ENVIRONMENT.get_template('templates/login.htm')
			self.response.write(template.render(template_values))
		else:
			if db.GqlQuery("SELECT * FROM Users WHERE username = '%s'" % User).count()==1:
				loggedUser = db.GqlQuery("SELECT * FROM Users WHERE username = '%s'" % User).get()
				loggedUserPassword=loggedUser.passhash
				if valid_pw(User,Pass,loggedUserPassword):
					usid=loggedUser.key().id()
					self.response.headers.add_header('Set-Cookie', 'userid=%s; Path=/; Max-Age=86400' % make_secure_val(usid))
					self.redirect("/blog/success")
				else:
					template_values = {"username": User,"password": "", "eusername":eu, "epassword":"invalid password"}
					template = JINJA_ENVIRONMENT.get_template('templates/login.htm')
					self.response.write(template.render(template_values))
			else:
				template_values = {"username": User,"password": "", "eusername":eu, "epassword":"no such user"}
				template = JINJA_ENVIRONMENT.get_template('templates/login.htm')
				self.response.write(template.render(template_values))

class RedirectPage(MyHandler):
	def get(self):
		self.redirect('/blog')

class LogoutPage(MyHandler):
	def get(self):
		self.response.headers.add_header('Set-Cookie', 'userid=; Path=/; Max-Age=86400')
		self.redirect('/blog/login')

class MapPage(MyHandler):
	def get(self):
		userhash=self.request.cookies.get('userid','DNE')
		if userhash=='DNE' or userhash=='' or not check_secure_val(userhash):
			self.redirect('/blog')
		else:
			posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC limit 5")
			markers=""
			for post in posts:
				logging.info(post.coords)
				if post.coords != None:
					markers=markers+"&markers="+str(post.coords.lat)+","+str(post.coords.lon)
			url = "http://maps.googleapis.com/maps/api/staticmap?size=800x600&sensor=false%s"%markers
			logging.info(url)
			urllib2.urlopen(url).read()
			loggedUser = Users.get_by_id(int(check_secure_val(userhash)))
			self.render("map.html",url=url,username=loggedUser.username)

class FlushPage(MyHandler):
	def get(self):
		memcache.flush_all()
		self.redirect('/blog')


application = webapp2.WSGIApplication([
	(r'^/blog/newpost/?$', NewPage),
	(r'^/blog/?(?:\.json)?', MainPage),
	(r'^/blog/(\d+)/?(?:\.json)?', EntryPage),
	(r'^/blog/signup/?$', SignupPage),
	(r'^/blog/success/?$', WelcomePage),
	(r'^/blog/login/?$', LoginPage),
	('/', RedirectPage),
	(r'^/blog/logout/?$', LogoutPage),
	(r'^/blog/map/?$', MapPage),
	(r'^/blog/flush/?$',FlushPage),
], debug=True)
