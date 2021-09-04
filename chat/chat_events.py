#!/usr/bin/env python
#!-*- coding: utf-8 -*-

# запуск: ./chat_events.py >> /var/log/ChatEvent.log 2>&1 &

import json, thread, sys, socket
from datetime import datetime

import tornado.web
import tornado.ioloop
import tornado.websocket
import tornado.httpserver
from tornado import template

from chat_db import *

domains = {'vashvizit.r':1, 'vashvizit.ru':2, 'rem-mastera.ru':3, 'kino-otzovik.ru':4}

class Connections():
  cons = {}
  cnt = 0
  def __init__(self):
    pass
  def addCon(self, uid, cookie, con, site):
    if not site in self.cons:
      self.cons[site] = {}    
    if not uid in self.cons[site]:
      self.cons[site][uid] = {}
      
    if len(self.UserSeances(site, uid))==0: # пользователь пришел
      SetUserState(uid, domains[site], 1)

    if cookie in self.cons[site][uid]:
      self.cons[site][uid][cookie]['pool'].append(con)
    else:
      self.cons[site][uid][cookie] = {'pool':[con], 't':datetime.now()}
      if isinstance(con, tornado.websocket.WebSocketHandler):
	self.cons[site][uid][cookie]['ip'] = con.request.remote_ip
    
    print uid, domains[site]
    cache = GetUserCache(uid, domains[site])
    if len(cache)>0:
      con.write_message(cache)

  def delCon(self, DelCon, uid, site):
    #for site in self.cons:
    #  for uid in self.cons[site]:
    if site in self.cons and uid in self.cons[site]:
	for cookie in self.cons[site][uid]:
	  for key,con in enumerate(self.cons[site][uid][cookie]['pool']):
	    if con==DelCon:
	      del self.cons[site][uid][cookie]['pool'][key]	      
	    
    self.cnt+=1
    if self.cnt%50==0:
      self.flush()
    
    if len(self.UserSeances(site, uid))==0: # пользователь ушел
      SetUserState(uid, domains[site], 2)    
	
  def flush(self):
    for site in self.cons:
      for uid in list(self.cons[site].keys()):
	u = self.cons[site][uid]
	if len(u)==0:
	  del u
	else:
	  for cookie in list(u.keys()):
	    if len(u[cookie]['pool'])==0:
	      del u[cookie]
	      if len(u)==0:
		del u

  def sendMsg(self, site, uid, msg):
    s = 0
    for wsock in self.UserSeances(site, uid):
      try:
	wsock.write_message(msg)
	s += 1
      except tornado.websocket.WebSocketClosedError as e:
	log('WebSocketClosedError:', e.strerror)
    SetUserCache(uid, domains[site], msg)
    #print msg
    return s
  
  def UserSeances(self, site, uid):	# find all seances of user
    r = []
    if site in self.cons and uid in self.cons[site]:
      u = self.cons[site][uid]
      for cookies in u:
	for WebSock in u[cookies]['pool']:
	  r.append(WebSock)
	  if False: 
	    break
    return r
  

def log(*st):
  print datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
  for s in st:
    print s,
  print
  sys.stdout.flush()

connections = Connections()

#c = 'c'
#connections.addCon(1,'asd', c, 'site.local')
#connections.addCon(1,'dsa', c, 'site.local')
#connections.addCon(2,'dss', c, 'site.local')
#print connections.cons,"\n"
#connections.delCon(c, 1, 'site.local')
#print connections.cons,"\n"
#connections.flush()
#print connections.cons,"\n"
#sys.exit()
#print connections.__dict__
#print connections.__class__



class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #db = self.application.db
        #messages = db.chat.find()
        self.render('index.html', messages=messages)
        

class WebSocket(tornado.websocket.WebSocketHandler):
  def check_origin(self, origin):
    if OriginToDomain(origin):
    #if origin in ('http://vashvizit.r', 'http://vashvizit.ru') or re.match(r'http://([\w\.]*)rem-mastera\.ru',origin) :    
      return True
    else:
      print 'origin=', origin

  def open(self):
    self.application.webSocketsPool.append(self)
    print 'open', self
    
    # keepalive settings for tcp socket
    self.stream.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    self.stream.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 120)
    self.stream.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)
    self.stream.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)

  def on_message(self, message):
    ##self.ws_connection.write_message('hello')    
    for value in self.application.webSocketsPool:
      if value != self:
	# value.ws_connection.write_message(message)
	pass

    dat = json.loads(message)
    print dat
    print self.request.headers['host']
    if 'iduser' in dat and 'sess_cookie' in dat:
      self.iduser = dat['iduser']
      connections.addCon(dat['iduser'], dat['sess_cookie'], self, OriginToDomain(self.request.headers['Origin']) )

  def on_close(self, message=None):
    for key, value in enumerate(self.application.webSocketsPool):
      if value == self:
	del self.application.webSocketsPool[key]

    try:
	connections.delCon(self, self.iduser, OriginToDomain(self.request.headers['Origin']) )
    except AttributeError as e:
	print e


def OriginToDomain(origin):
  d = origin.split('//')[1].split('.')
  d = d[-2]+'.'+d[-1]
  if domains.has_key(d):
    return d

def ToJSON(obj): # форматирование для отдачи черз json
  if isinstance(obj, datetime):
    return obj.strftime("%d.%m.%Y %H:%M:%S")
  if isinstance(obj, tornado.websocket.WebSocketHandler):
    return dict(ip=obj.request.remote_ip, rt=int(obj.request.request_time()), st=int(obj.request._start_time), UserAgent=obj.request.headers.get('User-Agent'))
  raise TypeError(repr(obj) + ' is not WebSocket')


def SendChatState(domain, uid, evt):
  log('SendChatState:',uid )
  try:
    return connections.sendMsg(domain, int(uid), evt)
  except:
    log ("SendChatState - error:", sys.exc_info()[0],'\n', sys.exc_info()[1] )

def ShowState():
  try:
    return json.dumps(connections.cons, default=ToJSON)
  except:
    log ("ShowState - error:", sys.exc_info()[0],'\n',sys.exc_info()[1] )   
 
def EventsSender():
  from SimpleXMLRPCServer import SimpleXMLRPCServer
  from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

  class RequestHandler(SimpleXMLRPCRequestHandler):
    def __init__(self, request, client_address, server):
      if client_address[0] in ('127.0.0.1', '192.168.0.101', '188.190.156.209', '81.177.141.32'):
	SimpleXMLRPCRequestHandler.__init__(self, request, client_address, server)
      else:
	log (' blocked ip: ', client_address)	

  server = SimpleXMLRPCServer(("0.0.0.0", 8765), requestHandler=RequestHandler)
  server.register_function(SendChatState, "SendChatState")
  server.register_function(ShowState)
  server.serve_forever()

class Application(tornado.web.Application):
  def __init__(self):
    self.webSocketsPool = []
    settings = {
      'static_url_prefix': '/static/',
    }
    handlers = (
      (r'/', MainHandler),
      (r'/websocket/?', WebSocket),
      (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'}),
    )
    tornado.web.Application.__init__(self, handlers)  

if __name__ == '__main__':
    thread.start_new_thread(EventsSender,())
    application = Application()

    #server = tornado.httpserver.HTTPServer(application, xheaders=True, ssl_options={"certfile":"/etc/httpd/winch-ssl/server.crt", "keyfile":"/etc/httpd/winch-ssl/server.key"})
    #server.listen(8787)  

    application.listen(8787)
    print 'chat events start'
    tornado.ioloop.IOLoop.instance().start()
