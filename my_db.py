# -*- coding: utf-8 -*-

import  MySQLdb, logging, time

#	charset='utf8',
#	use_unicode=True,
#	cursorclass=DictCursor

#cur = conn.cursor()
cur = conn.cursor(MySQLdb.cursors.DictCursor)
cur.execute("set names utf8")


class db:
	def __init__(self, TotalAttempts=7):
		self.TotalAttempts = TotalAttempts
		self.conn = None

	def query(self, sql, props=None):
		attempt = 0
		while True:
			try:
				if not self.conn:
					self.conn = MySQLdb.connect(host="localhost", db="admin", user="admin", passwd="***")
					self.cur = self.conn.cursor(MySQLdb.cursors.DictCursor)
					self.cur.execute("set names utf8")

				self.cur.execute(sql, props)
				return self.cur.fetchall()
			except MySQLdb.Error as e:
				#raise Exception(e)
				logging.warning (u'Неудачная попытка: %s. mysql error: %s ' % (attempt, e))
				if self.conn:
					self.conn.close()
					self.conn = None
				time.sleep(2.5)

			attempt	+= 1
			if attempt == self.TotalAttempts:
				raise Exception('не выполнен запрос с %d попыток' % (attempt))

	def commit(self):
		self.conn.commit()


if __name__ == "__main__":
	import wu
	wu.ConfLog(__name__)

	db1 = db()
	db1.query('asd')

	#for d in dir(conn):
	#	print d

	#if 'conn' in locals():
	#	print conn

	conn.close()
	del conn
	if 'conn' in locals():
		print (conn)




