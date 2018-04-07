#-*- coding: utf-8 -*-

# http://dev.mysql.com/downloads/connector/python/2.0.html
from mysql.connector import MySQLConnection, Error

class Column:
	def __init__(self):
		pass

	def __notnull(self,notnull):
		if notnull:
			return " NOT NULL"
		return ""

	def __column(self,fn,limit=None,offset=None,notnull=None):
		if limit is not None and offset is None:
			return "%s(%s) %s"%(fn.upper(),limit,self.__notnull(notnull))
		
		if limit is None and offset is None:
			return "%s %s"%(fn.upper(),self.notnull(notnull))
		
		if limit is not None and offset is not None:
			return "%s(%s,%s) %s"%(fn.upper(),limit,offset,self.__notnull(notnull))

	def increment(self):
		return "INT(11) AUTO_INCREMENT PRIMARY KEY"

	def int(self,limit,notnull=True):
		return self.__column("int",limit,None,notnull)

	def varchar(self,limit,notnull=True):
		return self.__column("varchar",limit,None,notnull)

	def text(self,notnull=True):
		return self.__column("text",None,None,notnull)

	def json(self,notnull=True):
		return self.__column("json",None,None,notnull)

	def boolean(self,notnull=True):
		return self.__column("boolean",None,None,notnull)

	def tinyint(self,notnull=True):
		return self.__column("tinyint",None,None,notnull)

	def smallint(self,notnull=True):
		return self.__column("smallint",None,None,notnull)

	def mediumint(self,notnull=True):
		return self.__column("mediumint",None,None,notnull)

	def decimal(self,limit,offset=0,notnull=True):
		return self.__column("decimal",limit,offset,notnull)

	def float(self,limit,offset=0,notnull=True):
		return self.__column("float",limit,offset,notnull)

	def real(self,limit,offset=0,notnull=True):
		return self.__column("real",limit,offset,notnull)

	def bit(self,limit,notnull=True):
		if limit is None or limit == 0:
			return self.__column("bit",None,None,notnull)
		return self.__column("bit",limit,None,notnull)

	def binary(self,limit,notnull=True):
		if limit is None or limit == 0:
			return self.__column("binary",None,None,notnull)
		return self.__column("binary",limit,None,notnull)



class MySQL:
	def __init__(self, host, database, user, password):
		self.config = dict()
		self.config['host'] = str(host)
		self.config['database'] = str(database)
		self.config['user'] = str(user)
		self.config['password'] = str(password)

		# Set to each query rows' count
		self.count = 0

		self.inserted_id = 0

		self.error_msg = ""

		self.col = Column()

	def usedb(self,db):
		self.config['database'] = str(db)

	def getConfig(self):
		return self.config

	def all(self, query, params=None):
		# query -> string
		# query -> tuple
		try:
			con = MySQLConnection(**self.config)
			cursor = con.cursor()
			if params is not None and isinstance(params, tuple):
				cursor.execute(str(query),params)
			elif params is not None and not isinstance(params, tuple):
				raise "params should be type tupe!"
			else:
				cursor.execute(str(query))
			self.count = cursor.rowcount
			self.inserted_id = 0
			return cursor.fetchall()
		except Error as e:
			return {}
			self.error_msg = e
		finally:
			cursor.close()
			con.close()

	def firstRow(self,query,params=None):
		return self.all(query,params)[0]

	def insert(self, table, d):
		try:
			con = MySQLConnection(**self.config)
			cursor = con.cursor()
			cursor.execute(self.__insert_query_generator(table,d))
			self.inserted_id = cursor.lastrowid
			con.commit()
			return True
		except Error as e:
			return {}
			self.error_msg = e
		finally:
			cursor.close()
			con.close()

	def delete(self, table, where=None):
		query = "DELETE FROM %s "%self.__where_check(where)
		
		return self.__commit(query)

	def update(self,table,d,where=None):
		query = "UPDATE %s SET "%(table)
		for column, value, comma in self.__iterable(d.iteritems()):
			query += "%s=%s%s"%(column,self.__val_checker(value),comma)
		query += self.__where_check(where)
		
		return self.__commit(query)

	def create(self,table,d,checkif=True):
		query = "CREATE TABLE %s `%s`("%(table,self.__checkif_check(checkif))
		for column, spec, comma in self.__iterable(d.iteritems()):
			query += "`%s` %s%s"%(column,self.__val_checker(spec),comma)
		query += ")"
		
		return self.__commit(query)

	def columnList(self,table):
		query = "SELECT column_name, column_type FROM information_schema.columns WHERE table_name = '%s'"%str(table)
		
		return self.all(query,None)

	def tableList(self):
		query = "SELECT table_name FROM information_schema.tables WHERE table_schema = '%s'"%str(self.config['database'])
		
		return self.all(query,None)


	def rawQuery(self,query):
		return self.__commit(query)

	def tableExist(self,name):
		query = "SELECT table_name FROM information_schema.tables WHERE table_schema = '%s' AND table_name = '%s'"%(str(self.config['database']),str(name))
		
		self.all(query,None)

		return self.__convert_true_false(self.count)

	def dbExist(self,name=None):
		if name is None:
			name = self.config['database']
		query = "SELECT * FROM information_schema.tables WHERE table_schema = '%s' GROUP BY table_schema"%str(name)
		
		self.all(query,None)

		return self.__convert_true_false(self.count)


	def __convert_true_false(self,chk):
		if chk > 0:
			return True
		return False

	def __checkif_check(self,check):
		if check:
			return "IF NOT EXISTS"
		return ""

	def __where_check(self,where):
		if where is not None:
			return "WHERE %s"%where
		else:
			return ""


	def __commit(self,query):
		try:
			con = MySQLConnection(**self.config)
			cursor = con.cursor()
			cursor.execute(str(query))
			con.commit()
			self.inserted_id = 0
			return True
		except Error as e:
			return {}
			self.error_msg = e
		finally:
			cursor.close()
			con.close()

	def __iterable(self,iterable):
		it = iter(iterable)
		last = next(it)

		for val in it:
			yield last, ", "
			last = val

		yield last, ""

	def __val_checker(self,inp):
		if isinstance(inp,str):
			return "'%s'"%inp
		elif isinstance(inp,int):
			return "%s"%inp

	def __col_val_with_comma_converter(self,d):
		result = ""
		for value, comma in self.__iterable(d.itervalues()):
			result += "%s%s"%(self.__val_checker(value),comma)
		return result

	def __insert_query_generator(self,table,d):
		if isinstance(d,list):
			query = ""
			for i,insert in enumerate(d):
				if i == 0: #first
					query = "INSERT INTO %s("%table
					for column, comma in self.__iterable(insert.iterkeys()):
						query += "`%s`%s"%(column,comma)

					query += ") VALUES("
					query += self.__col_val_with_comma_converter(insert)
					query += ")"
				else:
					#if i != len(d):
					query += ",("
					query += self.__col_val_with_comma_converter(insert)
					query += ")"
			return query

		elif isinstance(d,dict):
			query = "INSERT INTO %s("%table
			for column, comma in self.__iterable(d.iterkeys()):
				query += "`%s`%s"%(column,comma)

			query += ") VALUES("

			query += self.__col_val_with_comma_converter(d)

			query += ")"

			return query
		else:
			raise "should be data type dictionary or list in dictionaries"
