import webapp2
import random
import logging
import cgi

form="""
<form method="post">
<label>Month</label><input name="Month" value="%(month)s">
<label>Day</label> <input name="Day" value="%(day)s">
<label>Year</label> <input name="Year" value="%(year)s">
<input type="submit">
<div style="color: red">%(error)s</div>
</form>
"""

def valid_day(day):
    if day<32 and day>0:
        return True
    return False


def valid_month(month):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month=month[:3]
    for x in range(0, 11):
        if months[x]==month:
            return True
    return False

def valid_year(year):
    if(year>1900 and year<2017):
        return True
    return False
def escape_html(s):
    return cgi.escape(s, quote = True)



class MainPage(webapp2.RequestHandler):
    def write_form(self, error="", month="", day="", year=""):
        month=escape_html(month)
        self.response.headers['Content-Type']='text/html'
        self.response.write("When is your birthday?")
        self.response.write(form % {"error": error, "month": month,"day": day, "year": year})
    def get(self):
        self.response.headers['Content-Type']='text/html'
        self.write_form()
    def post(self):
        month = self.request.get("Month")
        #self.response.write(month)
        day = self.request.get("Day")
        #self.response.write(day)
        year = self.request.get("Year")
        #self.response.write(year)
        if valid_day(int(day)) and valid_month(month) and valid_year(int(year)):
            self.redirect("/success")
        else:
            self.write_form("That is not correct", month, day, year)

class SuccessPage(webapp2.RequestHandler):
    def get(self):
        self.response.write("Thanks! That's a totally valid day !!!")




application = webapp2.WSGIApplication([
    ('/', MainPage),   # maps the URL '/' to MainPage
    ('/success', SuccessPage)
], debug=True)

