#!/usr/bin/python
# -*- coding: utf-8 -*-

#def ami_event(event, manager):
#  print (event, manager)
#import panoramisk
#manager = panoramisk.Manager(host='127.0.0.1', port=5038, ssl=False, encoding='utf8')
#manager.connect()
#manager.register_event('Meetme*', ami_event)

from ast_functs import *

def event_PeerStatus(d):
  cur = MyCursor()
  disp = d['Peer'][4:]

  cur.execute("insert ignore into disp_active (disp) values (%s) " % (disp))    

  ss = {'Registered':('Address'), 'Unregistered':('Cause'), 'Unreachable':('Time'), 'Reachable':('Time'), 'Lagged':('Time')}[d['PeerStatus']]
  #print d['PeerStatus']
  #print ss
  #print d[ss]
  cur.execute("update disp_active set t=now(), d_status='%s', d_addit='%s' where disp=%s " % (d['PeerStatus'], d[ss], disp))
  cur.connection.commit() 

import socket

sock = socket.socket()
sock.connect(('localhost', 5038))

sock.send("Action: Login\r\n")
sock.send("UserName: winch\r\n")
sock.send("Secret: neworo\r\n\r\n")
#sock.send("Action: ListCommands\r\n\r\n")

while True:
  data = sock.recv(1024)
  if not data:
    break

  for bl in data.split("\r\n\r\n"):
    print '********'
    print bl
    d = {}
    for l in bl.split("\r\n"):
	v = l.split(": ")
	if len(v)>1:
	    d[v[0]] = v[1]
    if len(d)==0: continue
    print d

    if 'Event' in d:
	if d['Event']=='PeerStatus':
    	    print '------------',d['Peer'], d['PeerStatus']
    	    event_PeerStatus(d)
    	    if d['PeerStatus']=='Registered':
		print d['Address']
	    if d['PeerStatus']=='Unregistered':
		print d['Cause']

	if d['Event']=='ExtensionStatus':
		print d['Exten'], d['Status']

  
