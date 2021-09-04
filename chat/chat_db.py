#!/usr/bin/env python
#!-*- coding: utf-8 -*-

import MySQLdb
from datetime import datetime

def MyCursor():
  try:
    if datetime.now()-MyCursor.dt>3600:
      raise
  except:
    MyCursor.cur = MySQLdb.connect(host='localhost', db='', user='root', passwd='***').cursor()
    MyCursor.cur.execute("set names utf8")
    MyCursor.dt = datetime.now()
  return MyCursor.cur


def SetUserCache(uid, site, cache):
  cur = MyCursor()
  cur.execute("insert ignore into chat_user_cache (uid,site) values (%s,%s)" % (uid, site))
  cur.execute("update chat_user_cache set st_cache='%s', t_cache=now() where uid=%s and site=%s" % (cache, uid, site))


def GetUserCache(uid, site):
  cur = MyCursor()
  cur.execute("select st_cache from chat_user_cache where uid=%s and site=%s" % (uid, site))
  r = cur.fetchone()
  if r:
    return r[0]

def SetUserState(uid, site, st):
  cur = MyCursor()
  cur.execute("insert ignore into chat_user_cache (uid,site) values (%s,%s)" % (uid, site))
  cur.execute("update chat_user_cache set u_state=%s, t_state=now() where uid=%s and site=%s" % (st, uid, site))

