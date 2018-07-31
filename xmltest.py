import urllib2
response = urllib2.urlopen('http://www.example.com')
print response.headers['last-modified']
response = urllib2.urlopen('http://www.statesman.com')
print response.headers['server']
response = urllib2.urlopen('http://en.wikipedia.org/wiki/Python_(programming_language)')
print response.headers['age']
