#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
#sys.stderr = file("/tmp/p_err", "w+") 

from asterisk.agi import AGI
agi = AGI()

from ast_functs import *

if len(sys.argv)>1:
  action = sys.argv[1].strip()
  act2 = len(sys.argv)>2 and sys.argv[2].strip() or None
else:
  print "акция не указана"
  sys.exit()
  
#print action, act2    
FromNum = agi.get_variable("CALLERID(num)")

if action=="ReadCallNum":
  agi.set_variable("CallNum", ReadCallNum(FromNum))

elif action=="CallWent":
  if act2=="outgoing":
    IdCall = CallWent(agi.get_variable("CallNum"), 'out', disp=FromNum, masterId=agi.get_variable("master"), obj=agi.get_variable("obj"), type_obj=agi.get_variable("type_obj") )
    agi.set_variable("_direction", "outgoing")
  else:
    #agi.set_variable("CallNum", '1485')
    agi.set_variable("DialStr", GetDialStr())    
    (master,_ord) = FindPhone(FromNum)
    IdCall = CallWent(FromNum, 'in', masterId=master[0], obj=_ord, type_obj='ord')
    
  agi.set_variable("_IdCall", str(IdCall))
  agi.set_variable("RecName", '/var/opt/CallRec/ev%d.wav' % (IdCall))

elif action=="CallAnswer":
  CallAnswer(agi.get_variable("IdCall"), agi.get_variable("direction")=="outgoing", disp=agi.get_variable("DIALEDPEERNUMBER"))

elif action=="CallComplite":
  dialstatus = agi.get_variable("dialstatus")
  CallComplite(agi.get_variable("IdCall"), dialstatus, agi.get_variable("answeredtime"))
  if dialstatus=='ANSWER':
    #rename('/tmp/t'+FromNum+'.wav', '/var/opt/CallRec/ev'+IdCall+'.wav')
    pass

  
else:
  agi.execute("NoOp", "неизвестная акция")



#agi.answer()
#agi.say_date(10)
#v = agi.channel_status()

