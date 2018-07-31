import webapp2
import random
import logging
import cgi
import re
import jinja2
import os

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])


userre = re.compile(r"^([a-z0-9_\-A-Z]{3,20})");
passre = re.compile(r"^(.{3,20})");
emailre= re.compile(r"^(.{1,20}@.{1,20}\..{1,20})")





class MainPage(webapp2.RequestHandler):
	def write_form(self, eusername="", epassword="", everify="", eemail="", username="", password="", verify="", email=""):
		self.response.out.write(form % {"username": username,"password": password, "verify":verify, "email": email, "eusername":eusername, "everify":everify, "epassword":epassword,"eemail":eemail})
	
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		global template_values
		template_values = {"username": "","password": "", "verify":"", "email": "", "eusername":"", "everify":"", "epassword":"","eemail":""}
		template = JINJA_ENVIRONMENT.get_template('templates/index.htm')
		self.response.write(template.render(template_values))
	def post(self):
		success=True;
		eu="";
		ep="";
		ee="";
		ev="";
		global User
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
		template_values={"username": User,"password": Pass, "verify":Veri, "email": Emai, "eusername":eu, "everify":ev, "epassword":ep,"eemail":ee}
		if(success):
			self.redirect("/welcome");
		else:
			template = JINJA_ENVIRONMENT.get_template('templates/index.htm')
			self.response.write(template.render(template_values))

class WelcomePage(webapp2.RequestHandler):
	def get(self):
		template_values={"name":User}
		template = JINJA_ENVIRONMENT.get_template('templates/success.htm')
		self.response.write(template.render(template_values))
		#self.response.out.write(welcomehtml % {"name": User});


application = webapp2.WSGIApplication([
	('/', MainPage),   # maps the URL '/' to MainPage
	('/welcome', WelcomePage)
], debug=True)
