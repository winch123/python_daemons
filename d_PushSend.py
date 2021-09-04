#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, datetime, json, os, ssl, socket, requests, random, OpenSSL

def echo(*args):
	from bson import json_util	
	print '\n', datetime.datetime.today().strftime("%d %b - %H:%M:%S")
	#for m in inspect.stack():
	#	print m
	
	for a in args:
		#print type(a)
		if type(a) in (tuple, list, dict):
			print json.dumps(a, indent=4, ensure_ascii=False, default=json_util.default)
		else:
			print a


def mesAndroid(d, isOld):
	#### https://distriqt.github.io/ANE-PushNotifications/m.FCM-GCM%20Payload
	if isOld:
		m = {
            'alert':	d['title'],
            'title':	d['title'],
            'body':		d['body'],
            'notification':{
                "documentType": d['docType'],
                "params":	d['param'],
                'priority':0,
                'vibrate':True,
                'badge':0,
                "sound":'default'
            }
        }
	else:
		m = {
    	    'notification':{
                'alert'	:d['title'],
                'title'	:d['title'],
                'body'	:d['body'],
                "documentType" : d['docType'],
                "params" : d['param'], # ид заказа
                'priority' :0,
                'vibrate' :True,
                #'badge': 0,
                "sound": 'default',
                "colour": "#0000ff",
                #"backgroundImage" : "http://menuforme.online/files/8909/media/823/standard_1024_823_53b3123c3bd0b.png",
				#"backgroundImageTextColour" : "#FFFFFF",
				"style": {
					"type": "text", 
					"text": d['body'],
				},
            }
		}
		if 'link' in d and d['link'] != None:
			m['notification']['largeIcon'] = d['link']
			#m['notification']["backgroundImage"] = "http://menuforme.online/files/8909/media/823/standard_1024_823_53b3123c3bd0b.png"
			#m['notification']["backgroundImageTextColour"] = "#FFFFFF"
			echo(m)

	return m


def isAppOld(ns, ver):
    from distutils.version import LooseVersion, StrictVersion
    if ns[:26] == 'com.menu4me.richiepersonal':
		return StrictVersion(ver) < StrictVersion('3.15.22')
    elif ns[:18] == 'com.menu4me.dinner':
		return StrictVersion(ver) < StrictVersion('1.11.0')
		
    elif ns in ['ru.niagara74.app','com.menu4me.kitchen.sitiyoffice','com.menu4me.orders']:
		return False
    return True;

def sendPushAndroid(apiKey, devices, mes):
	echo('---- sendPushAndroid')	
	if apiKey == None:
		echo('apiKey in None')
		return { d:'NoneKey' for d in devices }

	try:			###	отправляем 
		resp = requests.post('https://android.googleapis.com/gcm/send',	
			data 	= json.dumps({'registration_ids':devices.values(), 'data':mes}),
			headers	= {'Authorization':'key='+apiKey, 'Content-Type':'application/json'},
			timeout = (3.3, 9)
			#verify=False
		)
	except (requests.exceptions.ReadTimeout, OpenSSL.SSL.WantWriteError) as e:
		#raise Exception('requests.exceptions.ReadTimeout: %s' % e)
		return { d:'GoogleTimeout' for d in devices }

	### парсим результаты отправок и сопостовляем их с входными devices	
	try:
		sRes = json.loads(resp.text)
		#echo(sRes)
		for i,token in enumerate(devices):
			#print token, sRes['results'][i]
			devices[token] = 'Success' if 'message_id' in sRes['results'][i] else sRes['results'][i]['error']
	except ValueError as e:
		echo('ValueError', resp.text)
		for token in devices:
			devices[token] = resp.text

	echo(devices)
	return devices
	
class MyException(Exception):
    pass

def sendPushIos(pem, topic, devices, title, body, docType, param):
	echo('---- sendPushIos')

	from apns2.client import APNsClient, apns2Exception
	from apns2.payload import Payload

	payload = Payload(alert={'title':title, 'body':body}, sound="default", custom={'documentType':docType, 'params':param}, badge=1)
	#echo(payload.dict())

	try:
		if not os.path.exists(pem):
			echo('не найден файл сертификата: %s' % pem)
			raise MyException('NoneCert')

		client = APNsClient(pem, use_sandbox=False, use_alternative_port=False)

		'''
		sends = [] 	# пакетная отправка (ещё не отлаженно)
		for token in devices.values():
			sends.append({'payload':payload, 'token':token})
		res = client.send_notification_batch(sends, topic)
		echo(res)
		'''

		for dev in devices:
			try:
				res = client.send_notification(devices[dev], payload, topic)
				echo(dev, devices[dev], res)
				devices[dev] = res
				#echo(token, res)
			except apns2Exception as e:
				echo('apns2Exception', type(e[0]), e[0])
				### могут прилететь исключения 2х типов: кортеж или строка
				devices[dev] = e[0][0] if type(e[0]) is tuple else e[0]

	except (MyException, ssl.SSLError, socket.error)  as e:
		#raise Exception('ssl problem: %s' % e)
		echo('problem: ', type(e), e)
		for dev in devices:
			devices[dev] = e


def sendPushFCM(api_key, devices, title, body, docType, param, link):
	echo('---- sendPushFCM')	

	#api_key = "AAAAU-mepRw:APA91bGlFSPx7xv1jVtOSDrxN56nNg8bIN20jmautkDUQVmUx2ZABBjnEz4GMRtuWs2_whEPDwzM2o043Cifwtay_R8SBgPBNoDLiju2fQKmKh7yw5cUs_rExOaCumsoWukluaRAXy7V"
	#fcm_id1 = "fFXary40p3Q:APA91bEucP8o-OWLi-91CsCKyfyzDLRU-NONl_oWt_9pFOi39nB017jvhNsD2HgGi6pXiLIDjAgC1936_4bAud6Bv0xawQiviw0AmilseKagfuaAsuc-WUWph4Bdn8VZiVYKaeEBfz3A"
	'''
	from pyfcm import FCMNotification
	push_service = FCMNotification(api_key=api_key)
	result = push_service.notify_multiple_devices(
		registration_ids	= devices.values(), 
		message_title	= unicode(title, 'utf8'), 
		message_body	= unicode(body, 'utf8'), 
		sound	= 'Default') 
	echo(result)
	'''

	try:
		resp = requests.post('https://fcm.googleapis.com/fcm/send',	
			headers	= {'Authorization':'key=' + api_key, 'Content-Type':'application/json'},
			data 	= json.dumps({
				'registration_ids': devices.values(), 
		        'notification'	: {
		        	'title' : title,
			        'text'  : body,
		        	'sound'	: 'default',
		        	#'badge'	: 0,
		        	#'click_action' : 'MY_INTENT',
		        },
	          	'data' : {
	            	"documentType" : docType,
	            	"orderId" : param,
	            	"newsId" : param,
	            	"sum"	: param,
	            	"image":	link,
	            	"uid": int(random.random()*1000000000),
		        	'title' : title,
			        'text'  : body,            	
	          	},
	          	"priority"  : 'high'
			}),	
			timeout = (3.3, 11)
			#verify=False
		)
	except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, OpenSSL.SSL.WantWriteError) as e:
		echo( type(e), e )  ### есть проблема: не печатается эсепшен.
		for token in devices:
			devices[token] = 'GoogleTimeout'
		#raise Exception(type(e) + '\n' + e )
		return

	try:
		sRes = json.loads(resp.text)
		echo(sRes)		
		for i,token in enumerate(devices):
			#print token, sRes['results'][i]
			devices[token] = 'Success' if 'message_id' in sRes['results'][i] else sRes['results'][i]['error']

	except ValueError as e:
		echo (resp.text)
		for token in devices:
			devices[token] = resp.text



def sssend():
	#from my_db import conn,cur, MySQLdb
	from my_db import db
	db1 = db(5)

	sql = '''SELECT m.id, m.title, m.body, m.docType, m.param, m.link, DATE_FORMAT(m.startAfter, '%d %M %H:%i:%S') _startAfter,
		gcm_send.deviceId, d.os, d.namespace, d.appVersion, d.account, a.account_id restId, 
		d.gcmToken, a.gcm_api_key, d.fcmToken, a.fcm_api_key
			from gcm_send
			join gcm_mess m on gcm_send.mesId = m.id
			join device d using (deviceId)
			join applications a on d.appId=a.id

				where gcm_send.sendState=1 
				and gcm_send.sendTime is null 
				and m.startAfter between DATE_ADD(now(), INTERVAL -2 hour) and now() 
				and (d.gcmStatus=1 or d.fcmStatus=1)
			LIMIT 202 '''
	sends = {}
	'''
	try:
		cur.execute(sql)
	except MySQLdb.Error as e:
		#raise Exception(e)
		echo ('mysql error', e)
		return 0	
	for m in cur.fetchall():
	'''

	for m in db1.query(sql):	
		#echo(m)

		if m['id'] not in sends: # формируем параметры пакета
			sends[m['id']] = { 'devs': {} }
			for f in ('title','body','docType','param','link','_startAfter','gcm_api_key', 'fcm_api_key', 'restId','namespace'):
				sends[m['id']][f] = m[f]

		if m['fcmToken'] == None: # формируем список получателей
			dos = m['os'] + (isAppOld(m['namespace'], m['appVersion']) and '_old' or '')
			token = m['gcmToken']
		else:
			dos = 'firebase'
			token = m['fcmToken']

		if dos not in sends[m['id']]['devs']:  
			sends[m['id']]['devs'][dos] = {}
		sends[m['id']]['devs'][dos][m['deviceId']] = token
				
	#conn.commit()
	db1.commit()
	#echo('было обнаружено %d сообщенй' % (len(sends))) 

	for mesId in sends:
		el = sends[mesId]
		echo(el)
		pem_file = '/var/www/vhosts/menuforme.online/httpdocs/www/files/%d/push/apns/ck.pem' % (el['restId'])

		for brand in el['devs']:
			devs = el['devs'][brand]

			if brand in ['android', 'android_old']:
				#sendPushAndroid(el['gcm_api_key'], devs, mesAndroid(el, brand=='android_old'))
				pass

			if brand in ['ios', 'ios_old']:
				sendPushIos(pem_file, el['namespace'], devs, el['title'], el['body'], el['docType'], el['param'])

			if brand == 'firebase':
				sendPushFCM(el['fcm_api_key'], devs, el['title'], el['body'], el['docType'], el['param'], el['link'])

			for t in devs:
				sql = "update gcm_send set result='%s', gcmToken='%s',sendTime=now() where mesId=%d and deviceId='%s' " % (devs[t], devs[t], mesId, t)
				#echo(sql)
				#cur.execute(sql)
				db1.query(sql)
			#conn.commit()
			db1.commit()

	return len(sends)

if __name__ == "__main__":
	import wu, logging
	wu.ConfLog(False, logging.WARNING)

	#sssend()
	#sys.exit()
	from daemon import Daemon

	class SendPushDaemon(Daemon):
		def run(self):
			echo('daemon start')
			while True:
				print '> > >'
				if 0 == sssend():
					print '< < <'
					time.sleep(22)				
	
	log_file = '/var/www/vhosts/menuforme.online/menuforme_logs/PushDaemon.log'
	pid_file = os.path.dirname(os.path.abspath(__file__)) + '/spd.pid'
	SendPushDaemon(pid_file, stdout=log_file, stderr=log_file).cmd()
