#! /opt/local/bin/python2.7

import httplib2
import re
import time

ENV1 = "http://10.0.0.254"
LABELS = ("G1T", "G1H", "G1W", "G3W", "G3H", "G3T", "G2T", "G2H", "G2W", "G4T", "G4H", "G4W")

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Env Mon</title>
<style>
    body {
        width: 35em;
        margin: 5 5;
        font-family: Tahoma, Verdana, Arial, sans-serif;
    }
</style>
<meta http-equiv="refresh" content="60">
</head>
<body>
<h1>T_out: %s &deg</h1>
<h1>T_att: %s &deg</h1>
<h3>H_out: %s </h3>
<img src="temperature.png"/>
<br/>
Updated: %s
</body>
</html>
"""

def getEm1Values(uri):
  h = httplib2.Http()
  _, resp = h.request(uri, "GET")
  values = re.findall(r'(\-?\d+\.\d)', resp[971:])
  return dict(zip(LABELS, values))

values = getEm1Values(ENV1)

print HTML % (values['G2T'], values['G1T'], values['G2H'], time.asctime())

#print "Attic   Temp: ", values['G1T']
#print "Humidity    : ", values['G2H']
