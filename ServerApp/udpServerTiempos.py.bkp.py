#!/usr/bin/python

# servidor udp
# ejemplo de la documentacion de python
# http://docs.python.org/2/library/socketserver.html
# modificado para permitir el registro del timestamp en la respuesta

import SocketServer
import datetime
import threading
import ConfigParser
import platform, os, sys, glob, shutil, time
import dbmanager
import rsa
import requests, webbrowser, json

from base64 import b64decode
from random import randrange


config = ConfigParser.ConfigParser()
config.read('/home/pfitba/tix_production/tixserver-deploy.cfg')
SERVER_HOST = config.get("TiXServer", "SERVER_HOST") #TODO: Change TEST!
SERVER_PORT = config.getint("TiXServer", "SERVER_PORT")
TEST_SERVER_HOST = config.get("TiXServer", "TEST_SERVER_HOST") #TODO: Change TEST!
TEST_SERVER_PORT = config.getint("TiXServer", "TEST_SERVER_PORT")
installDirUnix = config.get("TiXServer", "installDirUnix")
tixBaseUrl = config.get("TiXServer", "tixBaseUrl")

sys.path.append('/home/pfitba/tix_production/data_processing/')
import completo_III
sys.path.append('/home/pfitba/tix_production/ip_to_as/')
import info

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

# Logger examples
# logger.debug("debug message")
# logger.info("info message")
# logger.warn("warn message")
# logger.error("error message")
# logger.critical("critical message")

def ts():
  # time en microsegundos
  timestamp= datetime.datetime.now().strftime("%H:%M:%S:%f").split(':')
  en_microsegundos=float(timestamp[0])*3600*(10**6)+float(timestamp[1])*60*(10**6)+float(timestamp[2])*(10**6)+float(timestamp[3])
  #print timestamp
  #print en_microsegundos
  return str(int(en_microsegundos)) # <- en microsegundos, en hexa

# Devuelve los archivos segun su orden de modificacion
def get_files_by_mdate(dirpath):
    a = [os.path.join(dirpath, s) for s in os.listdir(dirpath)
         if os.path.isfile(os.path.join(dirpath, s))]
    a.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)))
    return a

# Dado un directorio y un archivo de log con nombre del estilo "log_timestamp", remueve todos los archivos
# mas viejos que una hora y cuarto del archivo pasado como parametro (utiliza el nombre de los archivos)
# para hacer la comparacion

def remove_old_files(dirpath, client_msg_filename):
  # Get all files in directory
  a = [os.path.join(s) for s in os.listdir(dirpath)
         if os.path.isfile(os.path.join(dirpath, s))]
  log_datetime = datetime.datetime.fromtimestamp(float(client_msg_filename.split("_")[1]))
  for file_name in a:
    try:
      curr_file_datetime = datetime.datetime.fromtimestamp(float(file_name.split("_")[1]))
      lapsed_time = (log_datetime-curr_file_datetime).total_seconds()
      try:
        if abs(lapsed_time) > 4500: #1.15 hs
          os.remove(dirpath + "/" + file_name)
          logger.info("Eliminando log antiguo: " + dirpath + "/" + file_name)

      except Exception, e:
        logger.error("No se ha podido eliminar el siguiente log antiguo: " + dirpath + "/" + file_name)
    except Exception, e:
     logger.error("El archivo de log tiene un nombre invalido: " + dirpath + "/" + file_name)

  return None


class ThreadingUDPRequestHandler(SocketServer.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        tstamp=ts()
        data = self.request[0].strip()
        socket = self.request[1]

        msg = data.split('!!')
        #este_thread=threading.current_thread()
        #threads_activos=threading.activeCount() #threading.enumerate()

        #print "{} wrote:".format(self.client_address[0])
        # print msg[0]+'|'+msg[1]+'|'+msg[2]+'1'+msg[3]

        if len(msg)>4:# depende de si es un mensaje corto o un mensaje largo
        #Mensaje largo
          socket.sendto(msg[0] + '|' + tstamp +'|' + str(ts()) + '|' + msg[3] + '|' + msg[4], self.client_address)
          try:
            #logger.info("Llamo thread " + str(threading.activeCount()))
            thread = threading.Thread(target = self.worker_thread, args=(msg,))
            thread.start()
            thread.join()
          except Exception, e:
            logger.info("Error: No se pudo iniciar el thread")
            logger.info(str(e))
        else:
        #Mensaje corto
          socket.sendto(msg[0]+'|'+ tstamp +'|' + str(ts()) + '|' + msg[3], self.client_address)

    def worker_thread(self, msg):
        large_package_msg = msg[4].split(';;')
        if len(large_package_msg)>=3 and large_package_msg[0]=='DATA':
          # Tengo datos para procesar dentro del mensaje largo
          #Cliente envia al server: DATA|publicKeyPlain|signedMeessage|msg
          client_pub_key_str_b64 = large_package_msg[1]
          client_pub_key_str = b64decode(large_package_msg[1])
          client_signed_msg = b64decode(large_package_msg[2])
          client_msg_filename = large_package_msg[3]
          client_plain_msg = b64decode(large_package_msg[4])

          logger.info("Se ha recibido el siguiente paquete de datos: " + client_msg_filename)
          # print "<public key>\n" + client_pub_key_str + "\n</public key>\n"
          # print "Signed msg: " + client_signed_msg
          # print "Filename: " + client_msg_filename
          # print "<plain msg>\n" + client_plain_msg + "\n</plain msg>\n"

          # En el servidor se hace el VERIFY, para esto se necesita tambien la firma!
          pubKey = rsa.PublicKey.load_pkcs1(client_pub_key_str)

          if rsa.verify(client_plain_msg, client_signed_msg, pubKey):
            logger.debug("Chequeo de integridad satisfactorio para " + client_msg_filename)
            client_data = dbmanager.DBManager.getInstallationAndClientId(client_pub_key_str_b64)

            if client_data is not None:
              installation_id = client_data[0]
              client_id = client_data[1]
              client_ip = str(self.client_address[0])

              #Client folder format: IP_cli_CLIENTID_ins_INSID
              client_server_folder = client_ip + "_cli_" + str(client_id) + "_ins_" + str(installation_id)
              logger.info("Salvando " + client_msg_filename + " en " + client_server_folder)
              client_records_server_folder = installDirUnix + "/records/" + client_server_folder
              if not os.path.exists(client_records_server_folder):
                logger.info("Creando directorio: " + client_server_folder)
                os.makedirs(client_records_server_folder)

              logFile = open(client_records_server_folder + "/" + client_msg_filename.split("/")[-1:][0], 'wb')
              logFile.write(client_plain_msg)
              logFile.close()

              # Check if there are old unusable files and remove them; we always need to keep only the REAL last hour of data
              remove_old_files(client_records_server_folder, client_msg_filename.split("/")[-1:][0])

              # Check if we have at least 1hr (twelve 5 minutes files) of data
              if len(os.walk(client_records_server_folder).next()[2]) == 60:
                logger.info("La instalacion " + client_server_folder + " tiene 1h de datos. Empezando procesamiento ...")

                # print "Starting calculation for the following files:"
                files_to_process = get_files_by_mdate(client_records_server_folder)

                # print files_to_process

                if len(files_to_process) < 60:
                  logger.error("Error al procesar los archivos de " + client_server_folder)
                else:
                  cwd = os.getcwd()
                  os.chdir('/home/pfitba/tix_production/data_processing')
                  ansDictionary = completo_III.analyse_data(files_to_process)
                  os.chdir(cwd)

                  # Remove 10 oldest logs
                  for count in range(0,9):
                    if os.path.isfile(files_to_process[count]) == True:
                      os.remove(files_to_process[count])
                  try:
                    new_isp_name = info.pais_num_name_nic(client_ip, 'EN' )[1]
                    logger.debug("ISP NAME = " + new_isp_name)
                  except Exception, e:
                    new_isp_name = 'Unknown'
                    logger.debug("ISP not found for IP: " + str(client_ip))
                  payload = {'isp_name': str(new_isp_name)}
                  headers = {'content-type': 'application/json'}

                  r = requests.post(tixBaseUrl + 'bin/api/newISPPost', data=json.dumps(payload), headers=headers)

                  jsonUserData = []

                  try:
                          jsonUserData = json.loads(r.text) # Parseo la respuesta JSON de la API de TiX
                  except Exception, e:
                          isp_id = 0

                  if(r is not None and len(jsonUserData) > 0):
                          isp_id = jsonUserData['id']
                  else:
                          logger.error("No se ha podido insertar el nuevo ISP en la DB, se utilizara default (" + client_server_folder + ")")
                          isp_id = 0

                  logger.debug("Intentando insertar nuevo record en la DB de la carpeta: " +  client_records_server_folder)
                  try:
                          dbmanager.DBManager.insert_record(ansDictionary['calidad_Down'],ansDictionary['utiliz_Down'],ansDictionary['H_RS_Down'],ansDictionary['H_Wave_Down'],time.strftime('%Y-%m-%d %H:%M:%S'),ansDictionary['calidad_Up'],ansDictionary['utiliz_Up'],ansDictionary['H_RS_Up'],ansDictionary['H_Wave_Up'],False,False,installation_id,isp_id,client_id)
                  except Exception, e:
                          logger.error("Error al insertar nuevo record en la DB de la carpeta: " + client_records_server_folder)
                          logger.error(e)

class ThreadingUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    pass


if __name__ == "__main__":
    logger.info("Validando existencia de directorios para los records")
    tix_server_path = "/etc/TIX"
    tix_server_records_path = "/etc/TIX/records"
    if not os.path.exists(tix_server_path):
      logger.info("Directorios inexistentes, creando directorios en: " + tix_server_path)
      os.makedirs(tix_server_path)
      os.makedirs(tix_server_records_path)

    HOST, PORT = TEST_SERVER_HOST, TEST_SERVER_PORT
#   HOST='127.0.0.1'
#   PORT=5005
    # Ctrl-C will cleanly kill all spawned threads
    daemon_threads = True
    # much faster rebinding
    allow_reuse_address = True
    # Create the server, binding to localhost on port 9999
    #server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
    server = ThreadingUDPServer((HOST, PORT), ThreadingUDPRequestHandler)

    #Threaded version
    server_thread= threading.Thread(target=server.serve_forever)
    logger.info("Starting server (" + str(HOST) + ":" + str(PORT) + ") thread " + server_thread.name)
    # server_thread.daemon = True
    server_thread.start()

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    #server.serve_forever()


