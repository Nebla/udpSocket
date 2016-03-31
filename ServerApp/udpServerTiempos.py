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
#import dbmanager
import rsa
import requests, webbrowser, json
import re
import linecache
from multiprocessing.pool import ThreadPool
from base64 import b64decode
from random import randrange

#import rollbar
#rollbar.init('a2f899737ec14e7bbe8a580f3fe94358', 'production')  # access_token, environment

config = ConfigParser.ConfigParser()

if len(sys.argv) < 2:
    configFilePath = '/home/pfitba/tix_production/tixserver-deploy.cfg'
else:
    configFilePath = sys.argv[1]

config.read(configFilePath)
SERVER_HOST      = config.get("TiXServer", "SERVER_HOST")
SERVER_PORT      = config.getint("TiXServer", "SERVER_PORT")
TEST_SERVER_HOST = config.get("TiXServer", "TEST_SERVER_HOST")
TEST_SERVER_PORT = config.getint("TiXServer", "TEST_SERVER_PORT")
installDirUnix   = config.get("TiXServer", "installDirUnix")
tixBaseUrl       = config.get("TiXServer", "tixBaseUrl")

sys.path.append('./data_processing/')
#import completo_III
sys.path.append('/home/pfitba/tix_production/ip_to_as/')
#import info

import logging

if len(sys.argv) < 3:
    logFilePath = '../var/tmp/tixUDPServerTiempos.log'
else:
    logFilePath = sys.argv[2]

# create logger
logger = logging.getLogger('udpServerTiempos')
hdlr = logging.FileHandler(logFilePath)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
hdlr.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

# add formatter to ch
hdlr.setFormatter(formatter)

# add ch to logger
logger.addHandler(hdlr)

def start():
    pass


from functools import wraps
import errno
import os
import signal

class TimeoutError(Exception):
    pass

class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)


from Queue import Queue
from threading import Thread

class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()
    
    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try: 
                func(*args, **kargs)
            except TimeoutError, e: 
                print "=== TIMEOUT ERROR" 
                print e
            except Exception, e: 
                print e

class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads):
        self.tasks = Queue(0)
        Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()

pool = ThreadPool(1)

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
    #files_to_delete = [f for f in os.listdir(dirpath) if re.match(r'log_*', f)]
    a = [os.path.join(s) for s in os.listdir(dirpath)
           if os.path.isfile(os.path.join(dirpath, s))]
    log_datetime = datetime.datetime.fromtimestamp(float(client_msg_filename.split("_")[1]))
    for file_name in a:
        try:
            curr_file_datetime = datetime.datetime.fromtimestamp(float(file_name.split("_")[1]))
            lapsed_time = (log_datetime-curr_file_datetime).total_seconds()
            try:
                if abs(lapsed_time) > 7200: #2 horas
                    os.remove(dirpath + "/" + file_name)
                    logger.info("Eliminando log antiguo: " + dirpath + "/" + file_name)

            except Exception, e:
                logger.error("No se ha podido eliminar el siguiente log antiguo: " + dirpath + "/" + file_name)
                #rollbar.report_exc_info()
        except Exception, e:
            logger.error("El archivo de log tiene un nombre invalido: " + dirpath + "/" + file_name)
            #rollbar.report_exc_info()

    return None

def remove_1h_files(dirpath):
    logger.info("Asegurando que la cantidad de logs en el directorio sea <= 60 para: " + dirpath)
    #files_to_delete = [f for f in os.listdir(dirpath) if re.match(r'log_*', f)]
    a = [os.path.join(s) for s in os.listdir(dirpath)
            if os.path.isfile(os.path.join(dirpath, s))]
    a.sort(key=lambda x: os.stat(os.path.join(dirpath, x)).st_mtime)
    while len(a) > 60:
        logger.debug('Hay ' + str(len(a)) + ' arhivos en el directorio ' + dirpath)
        file_to_remove = a.pop(0)
        logger.info("Eliminando log antiguo: " + dirpath + "/" + file_to_remove)
        os.remove(dirpath + "/" + file_to_remove)
        a.sort(key=lambda x: os.stat(os.path.join(dirpath, x)).st_mtime)

def get_last_line(fname):
        fh = open(fname, 'rb')
        for line in fh:
                pass
        last = line
        fh.close()
        return last

def get_oldest_file(dir):
        filelist = os.listdir(dir)
        filelist = filter(lambda x: not os.path.isdir(dir + "/" + x), filelist)
        return min(filelist, key=lambda x: os.stat(dir + "/" + x).st_mtime)

def get_newest_file(dir):
        filelist = os.listdir(dir)
        filelist = filter(lambda x: not os.path.isdir(dir + "/" + x), filelist)
        return max(filelist, key=lambda x: os.stat(dir + "/" + x).st_mtime)


class ThreadingUDPRequestHandler(SocketServer.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):

        try:
            tstamp=ts()
            data = self.request[0].strip()
            socket = self.request[1]
            print("Data recibida: " +data)
            msg = data.split('!!')
            #este_thread=threading.current_thread()
            #threads_activos=threading.activeCount() #threading.enumerate()

            #print "{} wrote:".format(self.client_address[0])
            # print msg[0]+'|'+msg[1]+'|'+msg[2]+'1'+msg[3]

            if len(msg)>4:# depende de si es un mensaje corto o un mensaje largo
                #Mensaje largo
                dataEnviada = msg[0] + '|' + tstamp +'|' + str(ts()) + '|' + msg[3] + '|' + msg[4]
                print("Mensaje largo: " + dataEnviada)
                socket.sendto(dataEnviada, self.client_address)
                try:
                    large_package_msg = msg[4].split(';;')
                    if len(large_package_msg)>=3 and large_package_msg[0]=='DATA':
                        pool.add_task(self.worker_thread, msg)
                except Exception, e:
                    logger.info("Error: No se pudo iniciar el thread")
                    logger.info(str(e))
                    #rollbar.report_exc_info()
            else:
            #Mensaje corto
                dataEnviada = msg[0]+'|'+ tstamp +'|' + str(ts()) + '|' + msg[3]
                print("Mensaje corto: " + dataEnviada)
                socket.sendto(dataEnviada, self.client_address)
        except:
            print("Error1")
            #rollbar.report_exc_info()

    def worker_thread(self, msg):
        print("Start worker thread!")
        try:
            large_package_msg = msg[4].split(';;')
            if len(large_package_msg)>=3 and large_package_msg[0]=='DATA':
                # Tengo datos para procesar dentro del mensaje largo
                #Cliente envia al server: DATA|publicKeyPlain|signedMeessage|msg
                client_pub_key_str_b64 = large_package_msg[1]
                client_pub_key_str = b64decode(large_package_msg[1])
                client_signed_msg = b64decode(large_package_msg[2])
                client_msg_filename = large_package_msg[3]
                client_plain_msg = b64decode(large_package_msg[4])

                # logger.info("Se ha recibido el siguiente paquete de datos: " + client_msg_filename)
                # # print "<public key>\n" + client_pub_key_str + "\n</public key>\n"
                # print "Signed msg: " + client_signed_msg
                # print "Filename: " + client_msg_filename
                # print "<plain msg>\n" + client_plain_msg + "\n</plain msg>\n"

                # En el servidor se hace el VERIFY, para esto se necesita tambien la firma!
                pubKey = rsa.PublicKey.load_pkcs1(client_pub_key_str)

                if rsa.verify(client_plain_msg, client_signed_msg, pubKey):
                    # logger.debug("Chequeo de integridad satisfactorio para " + client_msg_filename)
                    client_data = dbmanager.DBManager.getInstallationAndClientId(client_pub_key_str_b64)
                    # logger.debug("Se ha obtenido la siguiente client_data " + str(client_data))

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

                        # Check if we have more than 60 files, remove oldest till we get exactly 60 or less
                        remove_1h_files(client_records_server_folder)

                        # Check if we have at least 1hr (twelve 5 minutes files) of data
                        if len(os.walk(client_records_server_folder).next()[2]) == 60:
                            # logger.info("La instalacion " + client_server_folder + " tiene 1h de datos. Empezando procesamiento ...")
                            #
                            # logger.info("checkpoint 1")
                            # print "Starting calculation for the following files:"
                            files_to_process =  get_files_by_mdate(client_records_server_folder)
                            #files_to_process = [f for f in get_files_by_mdate(client_records_server_folder) if re.match(r'log_*', f)]

                            logger.info("checkpoint 2")

                            if len(files_to_process) < 60:
                                logger.error("Error al procesar los archivos de " + client_server_folder)
                            else:
                                # cwd = os.getcwd()
                                # os.chdir('/home/pfitba/tix_production/data_processing')
                                # logger.info("checkpoint 3")
                                print "Start analyse data"
                                ansDictionary = completo_III.analyse_data(files_to_process)
                                print "Finish analyse data"
                                # logger.info("checkpoint 4")
                                # logger.debug(ansDictionary)
                                # logger.info("checkpoint 5")
                                # os.chdir(cwd)
                                # logger.info("checkpoint 6")
                                #
                                #
                                # logger.info("Completando logs en " + "compare_timestamps_"+ client_records_server_folder+".log" )
                                # file_compare=open("/etc/TIX/records/logs_compare/" + "compare_timestamps_"+ client_server_folder+".log","a")
                                # logger.info("checkpoint 7")
                                # logger.info("oldest file: " + get_oldest_file(client_records_server_folder))
                                # oldest_line = linecache.getline( client_records_server_folder +"/"+ get_oldest_file(client_records_server_folder), 1)
                                # newest_line = get_last_line( client_records_server_folder +"/" + get_newest_file(client_records_server_folder))
                                # logger.info("oldest_line " + oldest_line)
                                # logger.info("newest_line " + newest_line)
                                # file_compare.write(oldest_line+"\n")
                                # file_compare.write(newest_line+"\n")
                                # file_compare.write("\n")
                                # file_compare.close()
                                # logger.info("Log completo" )

                                # Remove 10 oldest logs
                                for count in range(0,9):
                                    #if os.path.isfile(files_to_process[count]) == True and bool(re.match( "log_*",files_to_process[count])) == True:
                                    if os.path.isfile(files_to_process[count]) == True:
                                        os.remove(files_to_process[count])

                                try:
                                    new_isp_name = info.pais_num_name_nic(client_ip, 'EN' )[1]
                                    logger.debug("ISP NAME = " + new_isp_name)
                                except Exception, e:
                                    #rollbar.report_exc_info()
                                    new_isp_name = 'Unknown'
                                payload = {'isp_name': str(new_isp_name)}
                                headers = {'content-type': 'application/json'}
                                r = requests.post(tixBaseUrl + 'bin/api/newISPPost', data=json.dumps(payload), headers=headers)

                                jsonUserData = []

                                try:
                                    logger.debug("Parseo respuesta JSON de la API para newISPPost: " + str(jsonUserData))
                                    jsonUserData = json.loads(r.text) # Parseo la respuesta JSON de la API de TiX
                                except Exception, e:
                                    #rollbar.report_exc_info()
                                    isp_id = 0
                                if(r is not None and len(jsonUserData) > 0):
                                    isp_id = jsonUserData['id']
                                    logger.debug("Utilizando ISP = " + new_isp_name + " con ID = " + str(isp_id))
                                else:
                                    logger.error("No se ha podido insertar el nuevo ISP en la DB, se utilizara default (" + client_server_folder + ") |  jsonUserData: " + str(jsonUserData))
                                    isp_id = 0
                                logger.debug("Intentando insertar nuevo record en la DB de la carpeta: " +  client_records_server_folder)
                                try:
                                    dbmanager.DBManager.insert_record(ansDictionary['calidad_Down'],ansDictionary['utiliz_Down'],ansDictionary['H_RS_Down'],ansDictionary['H_Wave_Down'],time.strftime('%Y-%m-%d %H:%M:%S'),ansDictionary['calidad_Up'],ansDictionary['utiliz_Up'],ansDictionary['H_RS_Up'],ansDictionary['H_Wave_Up'],False,False,installation_id,isp_id,client_id)
                                except Exception, e:
                                    logger.error("Error al insertar nuevo record en la DB de la carpeta: " + client_records_server_folder)
                                    logger.error(e)
                                    #rollbar.report_exc_info()
                                print "---- SUCCESSFUL FINISH"
                    else:
                        logger.debug("No se ha podido obtener la client_data para la siguiente pubKey= " + str(client_pub_key_str_b64))
                else:
                    print("Problema con la clave")
        except Exception, e:
            print("Error 2")
            print(e)
            #rollbar.report_exc_info()

class ThreadingUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    pass


if __name__ == "__main__":
    logger.info("Validando existencia de directorios para los records")
    tix_server_path = "../ServerApp"
    tix_server_records_path = "../ServerApp/records"
    if not os.path.exists(tix_server_records_path):
        logger.info("Directorios inexistentes, creando directorios en: " + tix_server_path)
        #os.makedirs(tix_server_path)
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
    try:
        print ("Iniciando server en "+str(HOST)+":"+str(PORT))
        server = ThreadingUDPServer((HOST, PORT), ThreadingUDPRequestHandler)

        #Threaded version
        server_thread= threading.Thread(target=server.serve_forever)
        logger.info("Starting server (" + str(HOST) + ":" + str(PORT) + ") thread " + server_thread.name)
        # server_thread.daemon = True
        server_thread.start()
    except Exception as e:
        print(e)
        #rollbar.report_exc_info()


    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    #server.serve_forever()
