import psycopg2
import ConfigParser
import time

config = ConfigParser.ConfigParser()
config.read('/home/pfitba/tix_production/tixserver-deploy.cfg')
databaseName = config.get("TiXServer", "databaseName")
databaseHost = config.get("TiXServer", "databaseHost")
databasePort = config.get("TiXServer", "databasePort")
databaseUsername = config.get("TiXServer", "databaseUsername")
databasePassword = config.get("TiXServer", "databasePassword")

import logging
# create logger
logger = logging.getLogger('udpServerTiempos')
hdlr = logging.FileHandler('/var/tmp/tixUDPServerTiempos.log')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
hdlr.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

# add formatter to ch
hdlr.setFormatter(formatter)

# add ch to logger
logger.addHandler(hdlr)

class DBManager(object):
	INSTANCE = None

	def __init__(self):
		if self.INSTANCE is not None:
			raise ValueError("An instantiation already exists!")
		try:
			self.INSTANCE = psycopg2.connect(host=databaseHost,port=databasePort,user=databaseUsername,password=databasePassword,database=databaseName)
			self.INSTANCE.set_isolation_level(0)
	    	# conn = psycopg2.connect("dbname='template1' user='dbuser' host='localhost' password='dbpass'")
		except Exception, e:
			print "Error: I am unable to connect to the database!"
			print e

	@classmethod
	def get_instance(cls):
		if cls.INSTANCE is None:
			cls.INSTANCE = DBManager()
		return cls.INSTANCE

	def get_connection(self):
		if self.INSTANCE is None:
			self.INSTANCE = DBManager()
		return self.INSTANCE

	@classmethod
	def insert_record(cls, calidad_down,utiliz_down,h_rs_down,h_wave_down,timestamp,calidad_up,utiliz_up,h_rs_up,h_wave_up,userdowncongestion,userupcongestion,installation_id,isp_id,user_id):
		DBManagerInst = DBManager.get_instance()
		conn = DBManagerInst.get_connection()
		cursor = conn.cursor()
		try:
			cursor.execute("""INSERT INTO records(calidad_down,utiliz_down,h_rs_down,h_wave_down,timestamp,calidad_up,utiliz_up,h_rs_up,h_wave_up,userdowncongestion,userupcongestion,installation_id,isp_id,user_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", [calidad_down,utiliz_down,h_rs_down,h_wave_down,timestamp,calidad_up,utiliz_up,h_rs_up,h_wave_up,userdowncongestion,userupcongestion,installation_id,isp_id,user_id])
			logger.debug("[DBManager] Ejecutando la siguiente query en la DB (" + str(cursor.query) + ")")
			cursor.query
		except Exception, e:
			logger.error("[DBManager] No se ha podido insertar el record en la DB (" + str(cursor.query) + "): " + str(e))

	@classmethod
	def getInstallationAndClientId(cls, publicKey):
		DBManagerInst = DBManager.get_instance()
		conn = DBManagerInst.get_connection()
		cursor = conn.cursor()
		try:
			cursor.execute("""SELECT id, owner_id FROM installation WHERE encryptionkey=%s""", [publicKey])
			logger.debug("[DBManager] Intentando obtener el client_id y el installation_id (" + str(cursor.query) + ")")
			data = cursor.fetchone() # data[0] = installation_id, data[1] = user_id
			return data
		except Exception, e:
			logger.error("[DBManager] No se ha podido obtener el client_id y el installation_id (" + str(cursor.query) + ") de la siguiente publickey: " + str(publicKey) + " | " + str(e))

if __name__ == "__main__":
	# DBManager.insert_record(11100,20,53,'2013-04-14 16:20:12.345678',55,50,"false","false",1,1,1)
	#key = "LS0tLS1CRUdJTiBSU0EgUFVCTElDIEtFWS0tLS0tCk1FZ0NRUUN4MHlHNHp0bDhoMy9oSkNMNEVtZTBtdCtxM3Z4VWJ3LzV6MWFBTTJhWDBFRUpHQ3lsenUxNUwrdUUKZVhQWW8yYWF4dDhCZ0l1MWpMRlgrSnh0OGo5eEFnTUJBQUU9Ci0tLS0tRU5EIFJTQSBQVUJMSUMgS0VZLS0tLS0K"
	#key = "LS0tLS1CRUdJTiBSU0EgUFVCTElDIEtFWS0tLS0tCk1FZ0NRUUNKNUZEQlZqV3FsQUxVTzNpMEVaaXhzclBTSmEzc2M0UUhWMGFWVnhpc3dibU5yTndFUllKYmRocFUKM1ZlMHg0M1JXUmJoUUZVaFlwNzh2OEhCcU5OSEFnTUJBQUU9Ci0tLS0tRU5EIFJTQSBQVUJMSUMgS0VZLS0tLS0K"
	#key = "LS0tLS1CRUdJTiBSU0EgUFVCTElDIEtFWS0tLS0tCk1FZ0NRUUNGQzdMajRIbVY5cHVSZjdZSkVodFVHbWdpNFZVcXFLc0NPYlJTVkFqa0M3OHFzMXJXRllxQmRvK3YKdlVmMzcxbHNUU0VNYjFFMjJkZHlySkg1MHEwNUFnTUJBQUU9Ci0tLS0tRU5EIFJTQSBQVUJMSUMgS0VZLS0tLS0K"
	key = "LS0tLS1CRUdJTiBSU0EgUFVCTElDIEtFWS0tLS0tCk1FZ0NRUUNKNUZEQlZqV3FsQUxVTzNpMEVaaXhzclBTSmEzc2M0UUhWMGFWVnhpc3dibU5yTndFUllKYmRocFUKM1ZlMHg0M1JXUmJoUUZVaFlwNzh2OEhCcU5OSEFnTUJBQUU9Ci0tLS0tRU5EIFJTQSBQVUJMSUMgS0VZLS0tLS0K"
	key2 = """-----BEGIN RSA PUBLIC KEY-----
MEgCQQCgNdYXbjBaXkkHqcTUrUKLfVOTIw2IG248G1GBvoT4uHuSfgxrLf09H1DU
irG0ncvFZVdMworutHgcbWGUfY4HAgMBAAE=
-----END RSA PUBLIC KEY-----"""
	key3 = """-----BEGIN RSA PUBLIC KEY-----
MEgCQQDPy+46xqQe4fCFKEde3rBlQWJPu1YuhYW3xnORrIgsfo6XphuFXBeIyV7I
vnp1RBrZYnYWV2ml704ONkidCie3AgMBAAE=
-----END RSA PUBLIC KEY-----"""
	ansDictionary = {'H_RS_Up': 0.5972999999999999, 'H_RS_Down': 0.5974, 'calidad_Up': 1.0, 'utiliz_Down': 0.48666666666666664, 'H_Wave_Down': 0.5576, 'H_Wave_Up': 0.5185000000000001, 'utiliz_Up': 0.4633333333333334, 'calidad_Down': 0.9}
	#print DBManager.insert_record(ansDictionary['calidad_Down'],ansDictionary['utiliz_Down'],ansDictionary['H_RS_Down'],ansDictionary['H_Wave_Down'],time.strftime('%Y-%m-%d %H:%M:%S'),ansDictionary['calidad_Up'],ansDictionary['utiliz_Up'],ansDictionary['H_RS_Up'],ansDictionary['H_Wave_Up'],False,False,1,1,1)
	print DBManager.getInstallationAndClientId(key)
#	print DBManager.insert_record(calidad_down,utiliz_down,h_rs_down,h_wave_down,timestamp,calidad_up,utiliz_up,h_rs_up,h_wave_up,userdowncongestion,userupcongestion,installation_id,isp_id,user_id):
