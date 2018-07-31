import urllib2
from xml.dom import minidom
p = urllib2.urlopen("http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml")
x = minidom.parseString(p.read())
itemlist=x.getElementsByTagName("item")
print itemlist._get_length()
for i in itemlist:
    xitem=i
    xitemchild = xitem._get_childNodes()[1]
    title = xitem.childNodes[1]
    titleName= title.childNodes[0]
    print titleName.nodeValue
