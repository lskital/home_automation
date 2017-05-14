#! /usr/bin/python2.7

import httplib2
import re
import rrdtool
import time

ENV1 = "http://10.0.0.254"
ENV2 = "http://10.0.0.253"

RRDFILE = '/home/lskital/src/rrd/temperature.rrd'
RRDFILE2 = '/home/lskital/src/rrd/env2.rrd'
GRAPHFILE = '/home/lskital/src/rrd/gen/temperature.png'
HGRAPHFILE = '/home/lskital/src/rrd/gen/humidity.png'
HTMLFILE = '/home/lskital/src/rrd/gen/index.html'

RRDGRAPH_ARGS = [
  GRAPHFILE,
  '--legend-position=south', '-w 800', '-h 300', '--vertical-label=C',
  '--start=now-24h', '--step=60',
  'DEF:t_outdoor=%s:t_outdoor:AVERAGE' % RRDFILE,
  'DEF:t_attic=%s:t_attic:AVERAGE' % RRDFILE,
  'DEF:t_workshop=%s:t_env2:AVERAGE' % RRDFILE2,
  'LINE1:t_outdoor#00FF00:T_outdoor',
  'LINE1:t_attic#FF0000:T_attic',
  'LINE1:t_workshop#001DFF:T_workshop',
  ]

HRRDGRAPH_ARGS = [
  HGRAPHFILE,
  '--legend-position=south', '-w 800', '-h 300', '--vertical-label=%',
  '--start=now-24h', '--step=60', '--upper-limit=100',
  'DEF:h_outdoor=%s:h_outdoor:AVERAGE' % RRDFILE,
  'DEF:h_workshop=%s:h_env2:AVERAGE' % RRDFILE2,
  'LINE1:h_outdoor#00FF00:H_outdoor',
  'LINE1:h_workshop#001DFF:H_workshop',
  ]

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
<h1>T_wrk: %s &deg</h1>
<h3>H_wrk: %s </h3>
<h3>H_out: %s </h3>
<img src="temperature.png"/>
<img src="humidity.png"/>
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

class EnvMon():

  def update_rrd(self):
    rrdtool.update(
        RRDFILE, 
        "N:%s:%s:%s" % (self.values['G2T'], self.values['G1T'],
                        self.values['G2H']))
    rrdtool.update(
        RRDFILE2, 
        "N:%s:%s" % (self.values2['G1T'], self.values2['G1H']))

  def generate_graph(self):
    rrdtool.graph(*RRDGRAPH_ARGS)

  def generate_hgraph(self):
    rrdtool.graph(*HRRDGRAPH_ARGS)

  def generate_html(self):
    try:
      f = open(HTMLFILE, 'w')
      f.write(HTML % (
          self.values['G2T'], self.values['G1T'], self.values2['G1T'],
          self.values2['G1H'], self.values['G2H'], time.asctime()))
    except:
      raise

  def start(self):
    self.values = getEm1Values(ENV1)
    self.values2 = getEm1Values(ENV2)
    self.update_rrd()
    self.generate_graph()
    self.generate_hgraph()
    self.generate_html()


envmon = EnvMon()
envmon.start()




