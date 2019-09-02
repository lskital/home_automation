#! /usr/bin/python3

import httplib2
import re

ENV1 = "http://10.0.0.253"
LABELS = ("G1T", "G1H", "G1W", "G3W", "G3H", "G3T", "G2T", "G2H", "G2W", "G4T", "G4H", "G4W")

HTML = """

"""
def getEm1Values(uri):
  h = httplib2.Http()
  _, resp = h.request(uri, "GET")
  values = re.findall(r'(\-?\d+\.\d)', str(resp[971:]))
  return dict(zip(LABELS, values))

values = getEm1Values(ENV1)

print(values)
#print ("N:%s:%s:%s" % (values['G2T'], values['G1T'], values['G2H']))

#print "Attic   Temp: ", values['G1T']
#print "Humidity    : ", values['G2H']
