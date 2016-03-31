#!/usr/bin/python

import time
import datetime
import urllib
#import xmlrpclib
import socket
import logging
import subprocess
import binascii
import random
import threading
import sys
import ConfigParser
import rsa
import base64
import time, datetime, os

# Tomo data del archivo de configuracion
config = ConfigParser.ConfigParser()
config.read('/etc/TIX/app/udpclienttiempos.cfg')
installDirUnix = config.get("UDPClient", "installDirUnix")
HOST = config.get("UDPClient", "host")
PORT = config.getint("UDPClient", "port")
TEST_HOST = config.get("UDPClient", "TEST_host")
TEST_PORT = config.getint("UDPClient", "TEST_port")
TEST2_HOST = config.get("UDPClient", "TEST2_host")
TEST2_PORT = config.getint("UDPClient", "TEST2_port")
modo_debug = config.getint("UDPClient", "modo_debug")

def ts_filename():
    return time.time()

def ts():
    # time en microsegundos
    timestamp= datetime.datetime.now().strftime("%H:%M:%S:%f").split(':')
    en_microsegundos=float(timestamp[0])*3600*(10**6)+float(timestamp[1])*60*(10**6)+float(timestamp[2])*(10**6)+float(timestamp[3])
    return str(int(en_microsegundos)) # <- en microsegundos, en hexa


def relleno_largo(largo, check, told,log_file):
    if check == False:
        relleno=""
        for i in range(0,largo-1):
            relleno= relleno + str(random.randint(0,9))
    else:
        filereg=open(installDirUnix + "/app/" + log_file+told,"r")
        print("[" + datetime.datetime.fromtimestamp(time.time()).strftime('%d-%m-%Y %H:%M:%S') + "] Enviando paquete largo con DATA al servidor de medicion (" + filereg.name + ")...")
        msg = filereg.read()
        privateKeyFile = open(installDirUnix + '/tix_key.priv','r')
        publicKeyFile = open(installDirUnix + '/tix_key.pub','r')

        publicKey = rsa.PublicKey.load_pkcs1(publicKeyFile.read())
        privateKey = rsa.PrivateKey.load_pkcs1(privateKeyFile.read())

        signedMessage = rsa.sign(msg, privateKey, 'SHA-1')
        publicKeyPlain = publicKey.save_pkcs1(format='PEM')
        relleno = "DATA;;" + base64.b64encode(publicKeyPlain) + ";;" + base64.b64encode(signedMessage) + ";;" + filereg.name + ";;" + base64.b64encode(msg) + ";;"
        for i in range(len(relleno),largo-1):
            relleno= relleno + str(random.randint(0,9))
    return relleno


def log_msg(log_file, msg):
    arch=open(installDirUnix + "/app/"+ log_file,"a")
    print >>arch, datetime.datetime.now().strftime("%D|%H:%M:%S,%f"), msg
    arch.close()
    return



def pingUniq(num_uniq, logfile,t0, t0_filename, check,told):

    log_file = logfile + str(t0_filename)
    #deberian ser 12 bytes, 32 bits por cada timestamp (en hexa)
    _24hs='86400000000'

    t1 = _24hs
    t2 = _24hs
    t3 = _24hs
    t4 = _24hs

    #Mensaje corto

    t1 = ts()
    file_with_data = False
    relleno_largo_msg = ''

    if (num_uniq % 2 == 0) :
        message = t1 + '!!' + t2 + '!!' + t3 + '!!' + t4
    else:
        file_tobe_deleted = logfile + str(told)
        relleno_largo_msg = relleno_largo(4400,check,str(told),logfile)
        message = t1 + '!!' + t2 + '!!' + t3 + '!!' + t4 + '!!' + relleno_largo_msg
        file_with_data = relleno_largo_msg.startswith('DATA;;') # Para luego borrar el archivo una vez enviado

    client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    try:
        print("after read 0")
        client.settimeout(5.0)

        print("after read send")
        client.sendto(message + "\n", (TEST_HOST, TEST_PORT))
        if file_with_data == True:
            file_with_data = False
            #Delete data file
            if modo_debug == False:
                os.remove(installDirUnix + "/app/" + file_tobe_deleted)

        print("after read 0 recv")
        data = client.recv(8192) #(2048) para el mensaje largo
        print ("after read 1")
        msg = data.split('|')
        print("after read 2")
        data = msg[0] + '|' + msg[1] + '|' + msg[2] + '|' + ts() #+ '|' + msg[4], en msg[4] queda el contenido del mensaje largo sin imprimir

        print("after read 3")
        payload = 10
        iph=20 #longitud ip header (min. 20 bytes)
        udph=8 #longitud udp header (min. 8 bytes)

        if (num_uniq % 2 == 0) :
            payload=len(data) #longitud del mensaje en bytes
        else:
            payload=len(data + '|'+ msg[4])

        print("after read 4")
        pack_len=str(iph + udph + payload)
        log_msg(log_file, '|' + pack_len + '|' + data)

    #print data #debuging
    #msg_completo = str(data).split('|')
    #print len(data) #debuging
    except Exception as e:
        logging.exception(e)
        print("[" + datetime.datetime.fromtimestamp(time.time()).strftime('%d-%m-%Y %H:%M:%S') + "] Timeout: no hubo respuesta del servidor.")
        client.close()


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("usage: python <client>.py <logfile>\n")
        sys.exit()

    log_file=sys.argv[1]+'_'

    t0=ts()
    t0_filename = ts_filename()
    t0_date = datetime.datetime.fromtimestamp(t0_filename)
    t_old_filename = ''

    t_old = 0
    tries = 0
    i=0
    checker = False

    while True:
        #print i
        if tries <= 0:
            checker = False

        tnow = datetime.datetime.fromtimestamp(time.time())
        curr_lapsed_time = (tnow-t0_date).total_seconds()
        if (curr_lapsed_time > 60) or (curr_lapsed_time < 0): # 60 segundos o cambio de dia
            tries = 2
            t_old = t0
            t_old_filename = t0_filename
            checker = True
            t0=ts()
            t0_filename = ts_filename()
            t0_date = datetime.datetime.fromtimestamp(ts_filename()) # Asigno el nuevo t0 en el instante del procesamiento

        cliente= threading.Thread(target=pingUniq,args=(i,log_file,t0,t0_filename,checker,t_old_filename))
        cliente.start()
        #pingUniq(i, log_file)
        i=~i
        tries = tries - 1
        time.sleep(1)
