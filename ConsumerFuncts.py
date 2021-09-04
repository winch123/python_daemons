#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from my_db import conn, cur, MySQLdb
from my_db import db
db1 = db(3)

import re, urllib2, requests, logging, time, sys, json, datetime, os
from xml.dom import minidom
import wu

reload(sys)
sys.setdefaultencoding('utf-8')

def test1(p):
    #raise Exception('\xd1\x84\xd0\xb8\xd0\xb3-\xd0\xb2\xd0\xb0\xd0\xbc!')

    print ' [x] Received %r' % p
    time.sleep(2.5)
    print ' [x] Done %s' % p


def _LoadOrders(ids):
    sql1 = ''' SELECT os.id, os.clientName, os.clientPhone, os.created, os.paysystemId, 
        od.cityValue, od.streetValue, od.house, od.flat, od.floor, od.entrance, od.intercom, od.timeFrom, od.timeTo
        FROM order_system os
        LEFT JOIN order_delivery od ON os.id=od.order_system
        WHERE os.id IN (%s) '''
    logging.debug(sql1)
    #cur.execute(sql, ids)
    ords = {}
    #for o in cur.fetchall():
    for o in db1.query(sql1, ids):
        o['products'] = []
        ords[o['id']] = o    

    if len(ords)>0:
        sql2 = ''' SELECT po.productId, po.orderId, po.amount, po.price, getTranslate(i.Name, 'ru_ru') name, i.ExternalId
            FROM products_in_orders po
            JOIN item i ON i.id=po.productId
            WHERE po.orderId in (%s)'''

        #cur.execute(sql2, [ k for k in ords.keys() ])
        #for prods in cur.fetchall():
        for prods in db1.query(sql2, [ k for k in ords.keys() ]):
            ord1 = ords[prods['orderId']]
            ord1['products'].append(prods)

    logging.warning(wu.pretty(ords))
    return ords


def _setOrderProps(id, props):
    sql = 'UPDATE order_system SET %s WHERE id=%%(id)s' % ', '.join(('%s=%%(%s)s' % (k, k) for k in props.keys()))
    props.update({'id': id})
    logging.debug(sql, props)
    #cur.execute(sql, props)
    #conn.commit()
    db1.query(sql, props)
    db1.commit()


def _formatXML_FO_createOrd(o):
    from wu import minidomTag
    doc = minidom.Document()
    PayMethods = {1:100000009, 8:100000011, 16:2500000000 }

    root = minidomTag('xml', None, {'PayMethod': PayMethods[o['paysystemId']], 'QtyPerson': 1, 'Type': 1, 'PayState': 0, 'Remark': None, 'RemarkMoney': None, 
        'TimePlan': o['created'],
        'Brand': None, 'Department': 100000001, 'DiscountPercent': 0, 'OS': 'Android', 'Device': 'Samsung',  'Token': None})
    doc.appendChild(root)
    root.appendChild(minidomTag('Customer', None, {'Login': '', 'FIO': o['clientName']}))
    root.appendChild(minidomTag('Address', None, {'CityName': o['cityValue'],
     'StationName': None,
     'StreetName': o['streetValue'],
     'House': o['house'],
     'Corpus': None,
     'Building': None,
     'Flat': o['flat'],
     'Porch': o['entrance'],
     'Floor': o['floor'],
     'DoorCode': o['intercom']}))
    root.appendChild(minidomTag('Phone', None, {'Number': o['clientPhone']}))
    Products = minidomTag('Products')
    root.appendChild(Products)
    for product in o['products']:
        Products.appendChild(minidomTag('Product', None, {'Code': product['ExternalId'], 'Qty': product['amount']}))

    xml_str = doc.toprettyxml(indent='  ')
    return re.search('.+?\n(.+)', xml_str, flags=re.DOTALL).group(1)

FO_url = 'http://85.234.126.125:5060/FastOperator.asmx/'

def FastOperator_CreateOrder(dat):

    import pprint, json, HTMLParser
    ords = _LoadOrders( dat['ordId'] )
    xml = _formatXML_FO_createOrd(ords.values()[0])
    xml_request = FO_url + 'AddOrder?OrderText=&Order=' + urllib2.quote(xml)
    #logging.info(xml_request)

    resp = requests.get(xml_request).text
    #resp = '<string xmlns="www.fast-operator.ru">&lt;Order Code="080621" ID="619" /&gt;</string>'
    rrr = HTMLParser.HTMLParser().unescape(resp)
    logging.warning( rrr )

    ExtOrdId = minidom.parseString(rrr).getElementsByTagName('Order')[0].attributes['Code'].value
    _setOrderProps(dat['ordId'], {'externalId': ExtOrdId})

def FastOperator_SetPaymentSuccess(ExtOrdId):
    req = FO_url + 'SetPaymentSuccess?OrderID=%s' % ExtOrdId
    logging.info(req)
    resp = requests.get(req)
    logging.warning( resp.text )

def FastOperator_import(service, method, params):
    import subprocess
    #subprocess.call(["ls", "-l", "."])
    #stdout,stderr = subprocess.Popen(['php', 'functions.php', '123'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    stdout,stderr = subprocess.Popen(['php', 'functions.php', service, method, json.dumps(params)], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    logging.info(stdout)
    logging.info(stderr)
    with open('/tmp/FastOperator_import.json', 'w') as file: file.write(stdout)

    try:
        sRes = json.loads(stdout)
        logging.info(sRes)
    except ValueError as e:
        logging.warning('json ValueError')


def phpExec(d):
    service, method, params, sleep = d
    #print sleep
    import subprocess
    scriptDir = os.path.dirname(os.path.realpath(__file__))
    stdout,stderr = subprocess.Popen(['php', scriptDir+'/functions.php', service, method, json.dumps(params)], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    logging.info(stdout)
    logging.info(stderr)
    with open(scriptDir + '/../../../phpExec', 'a') as file:
        file.write('\n phpExec %s %s %s %s \n' %  (str(datetime.datetime.now()), service, method, params) )
        file.write(stdout)
    time.sleep(sleep)
    try:
        sRes = json.loads(stdout)
        logging.info(sRes)
        return sRes
    except ValueError as e:
        logging.warning('json ValueError')


def sushiplaza_CreateOrder():
    #url = 'http://rem-mastera.ru/test'
    url = 'http://admin.sushiplaza.ee/api/order/create'
    p = {
        'customer': {
            'email' : 'tt@test.com',
            'name' : 'test',
            'phone' : '123-456-789',
        }, 
        'items': [
            {'name':'sushi', 'amount':3 }
        ],
        'restaurant_name' : 'kalamaja',
        'comment' : '',
        'total' : '3',
    }
    resp = requests.post(url,  data = json.dumps(p), headers={'user-agent':'aaa', 
        'content-type':'application/json', 
        'x-authorization':'86b1d0b97f2e138a506796871ea6f3f9c71e1b57'} )
    logging.debug( resp.text )


if __name__ == '__main__':
    wu.ConfLog(False, logging.DEBUG)
    #FastOperator_CreateOrder({'ordId': 1453857})
    #FastOperator_SetPaymentSuccess('080621')
    
    #FastOperator_import()
    #FastOperator_import('ImportFromCSV', 'import_FastOperator', [48664])
    #FastOperator_import('AbstractDinner', '_loadOrder', [1793973])

    #sushiplaza_CreateOrder()

    #_LoadOrders( 1954907 )
    print 

    #phpExec('DinnerController', 'sendCompanyOrderTo', [1955163])

