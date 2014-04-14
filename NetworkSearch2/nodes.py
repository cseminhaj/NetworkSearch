import ConfigParser
import json
import urllib
import time
from sys import path
conf = ConfigParser.ConfigParser()
confwrite = ConfigParser.RawConfigParser()
conf.read(str(path[0])+'/nodes.cfg')
localhost = conf.get('host','location')

targethosts = conf.get('nodes','locations').split(',')

while 1:

  dist = ''
  for target in targethosts:
    url = 'http://maps.googleapis.com/maps/api/distancematrix/json?origins={'+target+'}&destinations={'+localhost+'}&mode=walking&language=en-EN&sensor=false'
    result = json.load(urllib.urlopen(url)) 
    nd = int(result['rows'][0]['elements'][0]['duration']['value'])
    dist = dist + str(nd) + ','

  dist = dist.rstrip(',')
  conf.set('nodes','distances',str(dist))

  with open(str(path[0])+'/nodes.cfg','wb') as configfile:
	     conf.write(configfile)

  time.sleep(86400)
