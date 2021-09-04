#!/usr/bin/env python
#!-*- coding: utf-8 -*-

import xmlrpclib, json, sys
import datetime

#adr = "http://217.113.115.237:8765"
adr = "http://188.190.156.209:8765"
#adr = "http://127.0.0.1/xmlrpc-serv.php"
proxy = xmlrpclib.ServerProxy(adr)

#from chat_db import *
#SetUserCache(1,1, 'sss')
#print GetUserCache(1,1)
#SetUserState(1,1,33)  
#sys.exit()


r = json.loads(proxy.ShowState())
for site in r:
  print '\n',site
  for u in  r[site]:
    print '   ',u
    for u1 in r[site][u]:
      print '     ',u1, ' \t ', r[site][u][u1]['ip'], ' | ', r[site][u][u1]['t']
      for u2 in r[site][u][u1]['pool']:
	#print '    ',u2
	print '        >',datetime.datetime.fromtimestamp(u2['st']), '-', u2['ip'],' #', u2['rt']
	#print '    ',u2['UserAgent']
print "\n"


