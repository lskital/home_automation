#! /opt/local/bin/python2.7

import httplib
import httplib2
import time
import socket


URL = "http://10.0.0.23"

def LocalException(Exception):
  pass

def getTemp():
  h = httplib2.Http()
  _, temp = h.request(URL, "GET")
  return temp

     

succ = 0
fail = 0
rr = [0,] * 10

while True:
  try:
    temp = getTemp()
    succ+=1
    rr.insert(0, temp)
    rr.pop()
  except httplib.BadStatusLine:
    temp = "Err" 
    fail+=1
  except socket.error as err:
    print "Socket Error: %s" % str(err)
    temp = "Err" 
    fail+=1
  print "%s: T: %s Success: %d, Fail: %d, Rate: %f\n" % (
      time.asctime(), str(temp), succ, fail, (float(succ)/(succ+fail)))

  time.sleep(1)

