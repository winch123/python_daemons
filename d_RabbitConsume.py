#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pika, time, sys, json, logging, threading, signal, traceback
#import importlib
#### __import__('send')
#### importlib.import_module('send')

reload(sys)
sys.setdefaultencoding('utf-8')

def importFuncts(module):
  w = __import__(module)
  ret = {}
  for name in dir(w):
    obj = w.__dict__.get(name)
    if name[0] != '_' and callable(obj) and obj.__module__ == module:
      #print name
      #print dir(obj)
      ret[name] = obj
  return ret

actions = importFuncts('ConsumerFuncts')
print '**** discovered actions:'
for action in actions:
  print '\t',action


def callback(ch, method, properties, body):
    #print (ch)
    #logging.warning(method.consumer_tag)
    #print (properties)
    try:
        body = json.loads(body)
    except ValueError as err:
        logging.critical('error: %s ' % (err))
    if 'action' in body:
      params = body['params'] if 'params' in body else None
      if body['action'] in actions:
        logging.warning('exec action: %s' % (body['action']))
        try:
	            actions[body['action']](params)
        except Exception as e:
          #raise Exception('!! problem: %s' % e)
          logging.critical( '!! problem: %s' % e )
          traceback.print_exception(*sys.exc_info())
      else:
        logging.critical('bad action: %s' % (body['action']))

    ch.basic_ack(delivery_tag = method.delivery_tag)

#channel.basic_qos(prefetch_count=1)
#channel.basic_consume('task_queue', callback)

#channel.start_consuming()
#sys.exit()

class consumerRabbitMQ(threading.Thread):

    def __init__(self, ProcNum, QueueName):
        threading.Thread.__init__(self)

        self.QueueName = QueueName
        self.ProcNum = ProcNum
        self.actions = importFuncts('ConsumerFuncts')

        # The shutdown_flag is a threading.Event object that indicates whether the thread should be terminated.
        self.shutdown_flag = threading.Event()

    def run(self):
      try:
        logging.warning('consumingRabbitMQ start')
        connection = pika.BlockingConnection(pika.ConnectionParameters( host='localhost', credentials=pika.PlainCredentials('winch', 'Qwe4ffew09')))
        channel = connection.channel()
        channel.queue_declare(queue=self.QueueName, durable=True)
        channel.basic_qos(prefetch_count=1)

        #channel.basic_consume(self.QueueName, callback)
        #channel.start_consuming()
        for message in channel.consume(self.QueueName, inactivity_timeout=1.5):
            if self.shutdown_flag.is_set():
                break
            method, properties, body = message
            if method:
              callback(channel, method, properties, body)
      except (pika.exceptions.AMQPConnectionError, pika.exceptions.ConnectionClosedByBroker) as e:
        self.shutdown_flag.set()
      finally:
        logging.warning('меня закрывают %s' % (self.ProcNum))


class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit of all running threads and the main program.
    """
    pass

def xmlrpc_serve():
	from xmlrpc.server import SimpleXMLRPCServer

	def is_even(n):
		return n % 2 == 0

	server = SimpleXMLRPCServer(("localhost", 8000))
	print("Listening on port 8000...")
	server.register_function(is_even, "is_even")
	server.serve_forever()


import wu
wu.ConfLog(__name__!='__main__', logging.WARNING)
#wu.ConfLog(__name__!='__main__', logging.INFO)
#wu.ConfLog(__name__!='__main__', logging.DEBUG)


def RunRabbitThreads():
    RabbitThreads = []
    try:
      for i,queueNane in {1:'task_queue', 2:'task_queue', 3:'task_queue', 56:'queue_for_iiko'}.items():
        print (i, queueNane)
        #threading.Thread(target=consumingRabbitMQ, args=()).start()
        t = consumerRabbitMQ(i, queueNane)
        t.start()
        RabbitThreads.append(t)

      while len(RabbitThreads) > 0: # Keep the main thread running, otherwise signals are ignored.
          time.sleep(0.7)
          for rt in RabbitThreads: # проверка внутренних исключений потоков
            if rt.shutdown_flag.is_set():
				RabbitThreads.remove(rt)
				#raise ServiceExit
      else:
        logging.warning('Уже все потоки завершились!')

    except ServiceExit:
      for rt in RabbitThreads:
        print rt
        rt.shutdown_flag.set()


def sig_handler(signal, frame):
    print('\nGot signal %d !' % (signal))
    raise ServiceExit

if __name__== '__main__':
    if len(sys.argv)>1 and sys.argv[1] == 'console':
        signal.signal(signal.SIGINT, sig_handler) ## Ctrl+C
        RunRabbitThreads()

    else:
        signal.signal(signal.SIGTERM, sig_handler)
        from daemon import Daemon

        class RabbitConsumeDaemon(Daemon):
            def run(self):
              RunRabbitThreads()

        log_file = '/var/logs/RabbitConsumeDaemon.log'
        RabbitConsumeDaemon('RabbitConsumeDaemon.pid', stdout=log_file, stderr=log_file).cmd()

