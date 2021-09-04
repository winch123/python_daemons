#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

def ReadCallNum(call):
  import os
  fn = "/var/opt/CallRec/f/%s" % call
  f = open(fn)
  ret = f.readline().strip()
  f.close()
  os.remove(fn)
  return ret


def MyCursor():
  try:
    if datetime.datetime.now()-MyCursor.dt>3600:
      raise
  except:
    import MySQLdb
    MyCursor.cur = MySQLdb.connect(host='localhost', db='vint_shpunt', user='root', passwd='***').cursor()
    MyCursor.cur.execute("set names utf8")
    MyCursor.dt = datetime.datetime.now()
  return MyCursor.cur

#def FindGreenOrder(disp, CustPhone):
#  cur = MyCursor()
#  cur.execute("""select o.id_ord from orders o
#    join orders_events oe on o.id_ord=oe.ord and oe.ev=1
#    where oe.disp=%s and o.status=1 and o.phone='%s' """ % (disp, CustPhone))
#  try:
#    return cur.fetchone()[0]
#  except:
#    return 0


def FindPhone(phone):
  cur = MyCursor()
  cur.execute(""" select u.u_id,u.u_name from rem_mastera.users u
    join rem_mastera.entity_options eo on u.u_id=eo.id_entity and type_entity='user' and opt=21
    where eo.val_str='%s' """ % (phone))
  master = cur.fetchone()
  _ord = ''
  if master==None:
    master = (0,'')
    cur.execute(" select * from orders where c_phone='%s' order by -id_ord limit 1")
    _ord = cur.fetchone()
    if _ord==None:
      _ord = ''
  return master, _ord

def GetDialStr():
  cur = MyCursor()
  cur.execute("select disp from disp_active where d_status in ('Registered','Reachable') and d_type=2 ")
  return '&'.join(['SIP/'+str(a[0]) for a in cur.fetchall()])


def CallWent(p_num, direction, disp='', masterId='', obj='', type_obj=''):
  cur = MyCursor()
  sql = "insert into calls_log (p_num,direction,disp,master,obj,type_obj) values ('%s','%s',0%s,0%s,0%s,'%s') " % (p_num, direction, disp, masterId, obj, type_obj)
  #print sql
  cur.execute(sql)
  cur.execute("select last_insert_id()")
  return cur.fetchone()[0]

def CallAnswer(EvId, outgoing, disp=''):
  sql = "update calls_log set answer_int=now()-t_call where id_call=%s " % (EvId)
  #print sql
  MyCursor().execute(sql)
  if not outgoing:
    MyCursor().execute("update calls_log set disp=%s where id_call=%s " % (disp, EvId))

def CallComplite(EvId, dialstatus, answeredtime):
  sql = "update calls_log set dialstatus='%s', " % (dialstatus)
  sql += answeredtime=='' and "answer_int=now()-t_call" or "talk_int=now()-t_call-answer_int, talk_int_=%s" % (answeredtime)
  sql += "  where id_call=%s" % (EvId)
  MyCursor().execute(sql)


if __name__ == "__main__":
  #ThrowEvent(123, 11, '', 1)
  #print ReadCallNum('1485')
  #print FindGreenOrder(1, '79999999999')
  #print CallWent('123', disp='', _ord='')
  #CallAnswer(5, True, 7)
  #CallComplite(3, 'ANSWER', '')
  #print GetDialStr()
  (master,_ord) = FindPhone("79033771455")
  print master[1]

