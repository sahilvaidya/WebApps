import urllib2
from xml.dom import minidom
def get_coords(ip):
    p = urllib2.urlopen("http://freegeoip.net/xml/"+str(ip))
    x = minidom.parseString(p.read())
    res = x.childNodes[0]
    #print res.getElementsByTagName("Latitude")[0].childNodes[0].nodeValue
    latitude= res.getElementsByTagName("Latitude")[0].childNodes[0].nodeValue
    longitude=res.getElementsByTagName("Longitude")[0].childNodes[0].nodeValue
    print "("+latitude+","+longitude+")"

get_coords("192.107.137.120")
    
