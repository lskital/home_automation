#! /usr/bin/python3
from pyephember import pyephember

import argparse
import httplib2
import re
import rrdtool
import time
import sys

#ENV1 = "http://10.0.0.254"
ENV2 = "http://10.0.0.253"

RRDFILES = {
        't_water': "/home/lskital/rrd/t_water.rrd",
        't_upstairs': "/home/lskital/rrd/t_upstairs.rrd",
        't_downstairs': "/home/lskital/rrd/t_downstairs.rrd",
        't_workshop': "/home/lskital/rrd/t_workshop.rrd",
        'h_workshop': "/home/lskital/rrd/h_workshop.rrd",
}        

WATER_GRAPHFILE = '/home/lskital/rrd/gen/water.png'
ROOM_GRAPHFILE = '/home/lskital/rrd/gen/temperature.png'
HGRAPHFILE = '/home/lskital/rrd/gen/humidity.png'
HTMLFILE = '/home/lskital/rrd/gen/index.html'

ROOMGRAPH_ARGS = [
  ROOM_GRAPHFILE,
  '--legend-position=south', '-w 800', '-h 300', '--vertical-label=C',
  '--start=now-24h', '--step=60',
  #'DEF:t_outdoor=%s:t_outdoor:AVERAGE' % RRDFILE,
  #'DEF:t_attic=%s:t_attic:AVERAGE' % RRDFILE,
  'DEF:t_workshop=%s:value:AVERAGE' % RRDFILES['t_workshop'],
  'DEF:t_upstairs=%s:value:AVERAGE' % RRDFILES['t_upstairs'],
  'DEF:t_downstairs=%s:value:AVERAGE' % RRDFILES['t_downstairs'],
  #'LINE1:t_outdoor#00FF00:T_outdoor',
  #'LINE1:t_attic#FF0000:T_attic',
  'LINE1:t_workshop#001DFF:T_workshop',
  'LINE1:t_upstairs#F200FF:T_upstairs',
  'LINE1:t_downstairs#00FFCC:T_downstairs',
  ]

WATERGRAPH_ARGS = [
  WATER_GRAPHFILE,
  '--legend-position=south', '-w 800', '-h 300', '--vertical-label=C',
  '--start=now-24h', '--step=60',
  'DEF:t_water=%s:value:AVERAGE' % RRDFILES['t_water'],
  'LINE1:t_water#001DFF:T_water',
  ]

HRRDGRAPH_ARGS = [
  HGRAPHFILE,
  '--legend-position=south', '-w 800', '-h 300', '--vertical-label=%',
  '--start=now-24h', '--step=60', '--upper-limit=100',
  #'DEF:h_outdoor=%s:h_outdoor:AVERAGE' % RRDFILE,
  'DEF:h_workshop=%s:value:AVERAGE' % RRDFILES['h_workshop'],
  #'LINE1:h_outdoor#00FF00:H_outdoor',
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
<h1>T_water: %s &deg</h1>
<h1>T_up: %s &deg</h1>
<h1>T_down: %s &deg</h1>
<h1>T_wrk: %s &deg</h1>
<h3>H_wrk: %s </h3>
<img src="water.png"/>
<img src="temperature.png"/>
<img src="humidity.png"/>
<br/>
Updated: %s
</body>
</html>
"""

EMBER_ZONE_MAP = {
  'Downstairs': 't_downstairs',
  'Upstairs': 't_upstairs',
  'Hot Water': 't_water',
}

def getEm1Values(uri):
  h = httplib2.Http()
  _, resp = h.request(uri, "GET")
  values = re.findall(r'(\-?\d+\.\d)', str(resp[971:]))
  return dict(zip(LABELS, values))

def getEmberValues(email, password):
  emb = pyephember.EphEmber(email, password)
  home = emb.get_home()
  if not home['isSuccess']:
    print(home['message'])
    return dict()
  result = dict()
  for rec in home['data']['receivers']:
    for zone in rec['zones']:
      result[EMBER_ZONE_MAP[zone['name']]] = zone['currentTemperature']
  return result

class EnvMon():

  values_dict = dict();

  def __init__(self, email, password):
      self.email = email
      self.password = password

  def _update_one_rrd(self, filename, value):
    rrdtool.update(filename, "N:%s" % value)

  def update_rrd(self):
      for name, value in self.values_dict.items():
          self._update_one_rrd(RRDFILES[name], value)

  def update_rrd_obsolete(self):
    rrdtool.update(
        RRDFILE, 
        "N:%s:%s:%s" % (self.values['G2T'], self.values['G1T'],
                        self.values['G2H']))
    rrdtool.update(
        RRDFILE2, 
        "N:%s:%s" % (self.values2['G1T'], self.values2['G1H']))

  def generate_room_graph(self):
    rrdtool.graph(*ROOMGRAPH_ARGS)

  def generate_water_graph(self):
    rrdtool.graph(*WATERGRAPH_ARGS)

  def generate_hgraph(self):
    rrdtool.graph(*HRRDGRAPH_ARGS)

  def generate_html(self):
    try:
      f = open(HTMLFILE, 'w')
      f.write(HTML % (
          self.values_dict['t_water'],
          self.values_dict['t_upstairs'],
          self.values_dict['t_downstairs'],
          self.values_dict['t_workshop'],
          self.values_dict['h_workshop'],
          time.asctime()))
    except:
      raise

  def start(self):
    env_values = getEm1Values(ENV2)

    self.values_dict['t_workshop'] = env_values['G1T']
    self.values_dict['h_workshop'] = env_values['G1H']

    emb_values = getEmberValues(self.email, self.password)

    self.values_dict.update(emb_values)

    self.update_rrd()
    self.generate_water_graph()
    self.generate_room_graph()
    self.generate_hgraph()
    self.generate_html()
    #print(self.values_dict)

def main():
  parser = argparse.ArgumentParser(prog='env_update', description='')
  parser.add_argument("--email", type=str,
                      help="Email Address")
  parser.add_argument('--password', type=str, default="",
                      help="Password")
  args = parser.parse_args()
  envmon = EnvMon(args.email, args.password)
  envmon.start()


if __name__ == '__main__':
        sys.exit(main())
