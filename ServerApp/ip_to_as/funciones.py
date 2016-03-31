#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import MySQLdb as mdb
from unicodedata import normalize

################################
# funciones para base de datos #
################################
def conectardb():
    db_host = 'localhost'
    usuario = 'root'
    clave = '54bf1n6'
    base_de_datos = 'ip_to_as'
    conndb = mdb.connect(host=db_host, user=usuario, passwd=clave, db=base_de_datos)
    cursor = conndb.cursor()
    return cursor, conndb

def findpaisxip(octeto):
    '''
    busca paises del nic (lacnic, ripe, arin, afrinic, apnic) que coincidan con la ip que comience con el primer octeto indicado
    '''
    cursor, conndb = conectardb()
#    sql = 'SELECT pais_' + nic + ' AS pais, ip_' + nic + ' AS ip, host_' + nic + ' AS host from ' + nic + ' WHERE ip_' + nic + ' regexp "^' + octeto + '\\.";'

    sql = 'SELECT * FROM afrinic where afrinic.ip_afrinic regexp "^' + octeto + '\\." UNION SELECT * FROM apnic WHERE apnic.ip_apnic regexp "^' + octeto + '\\." UNION SELECT * FROM arin WHERE arin.ip_arin regexp "^' + octeto + '\\." UNION SELECT * FROM lacnic WHERE lacnic.ip_lacnic regexp "^' + octeto + '\\." UNION SELECT * FROM ripe WHERE ripe.ip_ripe regexp "^' + octeto + '\\.";'

    cursor.execute(sql)
    resultado=cursor.fetchall()
    cursor.close()
    conndb.close()
    if len(resultado) == 0:
        lstpasixip = ['UNKNOWN']
    else:    
        lstpasixip=[]
        for valor in resultado:
            pais = valor[1]
            ip = valor[2]
            host = str(valor[3])
            lstpasixip.append(ip + '\t' + host + '\t' + pais)
    return lstpasixip

def findasxip(octeto):
    '''
    busca numero de as que coincidan con la ip que comience con el primer octeto indicado
    '''
    cursor, conndb = conectardb()
    sql = 'SELECT noderouter AS numas, ip_router AS ip, mask FROM routerviews WHERE ip_router regexp "^' + octeto + '\\.";'

    cursor.execute(sql)
    resultado=cursor.fetchall()
    cursor.close()
    conndb.close()
    lstasxip=[]
    if len(resultado) == 0:
        lstasxip = 'UNKNOWN'
    else:   
        for valor in resultado:
            numas = str(valor[0])
            ip = valor[1]
            mask = str(valor[2])
            lstasxip.append(numas + '\t' + ip + '\t' + mask)
    return lstasxip

def findnicxas(num_as):
    cursor, conndb = conectardb()
    sql = 'SELECT nic from paisnodes where nodep=' + num_as+ ' group by nic;'

    cursor.execute(sql)
    resultado=cursor.fetchall()
    cursor.close()
    conndb.close()
#    print resultado
    if len(resultado) == 0:
        resultado = 'UNKNOWN'
    else:
        resultado = resultado[0][0]
    return resultado

def findnombrexas(num_as):
    '''
    busca nimbre de as que coincidan con el numero de as indicado
    '''
    cursor, conndb = conectardb()
    sql = 'SELECT name FROM namenodes WHERE noden = ' + num_as+ ';'

    cursor.execute(sql)
    resultado=cursor.fetchall()
    cursor.close()
    conndb.close()
#    print resultado
    if len(resultado) == 0:
        resultado = 'UNKNOWN'
    else:
        resultado = resultado[0][0]
    return resultado

def selectpaisname(codigopais, idioma='langEN'):
    '''
    devuelve el nombre del pais a partir del codigo de 2 letras en ingles o spanish  
    idioma langEN (ingles), langES (spanish)  
    '''
    cursor, conndb = conectardb()
    cursor.execute('SELECT ' + idioma + ' FROM countries WHERE alpha2 = "' + codigopais + '" ;')
    resultado=cursor.fetchall()
    cursor.close()
    conndb.close()
    if len(resultado) == 0:
        resultado = False
    else:
        resultado = resultado[0][0]
    return resultado

def listapaises(idioma='EN'):
    cursor, conndb = conectardb()


    cursor.execute('SELECT alpha2, lang' + idioma + ' FROM countries INNER JOIN (SELECT nodeA, pais FROM (SELECT nodeA FROM linknodes UNION SELECT nodeB FROM linknodes) AS nodealias INNER JOIN paisnodes ON nodep=nodeA GROUP BY nodeA) AS alias ON pais=alpha2 group by lang' + idioma + ';')

#    cursor.execute('SELECT alpha2, lang' + idioma +' FROM countries INNER JOIN paisnodes ON pais=alpha2 GROUP BY lang' + idioma + ';')
    resultado=cursor.fetchall()
    #print resultado
    cursor.close()
    conndb.close()
    if len(resultado) == 0:
        resultado = False
    else:
        salida = resultado
    return salida
    
def nodos_x_pais_o_nic(buscapor=''):
    '''
    devuelve lista de nodos por pais o por nic (afrinic, apnic, arin, lacnic, ripe) si es vacio devuelve todos
    '''

    cursor, conndb = conectardb()
    if buscapor in ['afrinic', 'apnic', 'arin', 'lacnic', 'ripe']:

        ### devuelve tabla de enlaces de nodos a partir de la red completa donde ambos nodos perteneces al pais elejido
        sqlred = 'SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '");'

        ### devuelve tabla nodos y pais que estan en la red completa y que pertenecen al pais elejido 
        sqlpaises = 'SELECT nodeA AS node, pais, nic FROM (SELECT nodeA FROM (SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '")) AS redpais1 UNION SELECT nodeB FROM (SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '")) AS redpais2) AS listapais INNER JOIN paisnodes ON nodep=listapais.nodeA ORDER BY node;'

        ###devuelve los nombres de los nodos de la red perteneciente al pais elegido si hay un nodo del pais que no tiene nombre devuelve un string vacio como nombre,
        sqlnombres = 'SELECT nodeA AS node, IFNULL(name,"") AS nombre FROM (SELECT nodeA FROM (SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '")) AS redpais1 UNION SELECT nodeB FROM (SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE nic="' + buscapor + '")) AS redpais2) AS listapais LEFT JOIN namenodes ON noden=listapais.nodeA ORDER BY node;'

        
    else:
        ### devuelve tabla de enlaces de nodos a partir de la red completa donde ambos nodos perteneces al pais elejido
        sqlred = 'SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '");'

        ### devuelve tabla nodos y pais que estan en la red completa y que pertenecen al pais elejido 
        sqlpaises = 'SELECT nodeA AS node, pais, nic FROM (SELECT nodeA FROM (SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '")) AS redpais1 UNION SELECT nodeB FROM (SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '")) AS redpais2) AS listapais INNER JOIN paisnodes ON nodep=listapais.nodeA ORDER BY node;'

        ###devuelve los nombres de los nodos de la red perteneciente al pais elegido si hay un nodo del pais que no tiene nombre devuelve un string vacio como nombre,
        sqlnombres = 'SELECT nodeA AS node, IFNULL(name,"") AS nombre FROM (SELECT nodeA FROM (SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '")) AS redpais1 UNION SELECT nodeB FROM (SELECT nodeA, nodeB, frec FROM linknodes WHERE nodeA IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '") AND nodeB IN (SELECT nodep FROM paisnodes WHERE pais="' + buscapor + '")) AS redpais2) AS listapais LEFT JOIN namenodes ON noden=listapais.nodeA ORDER BY node;'

    cursor.execute(sqlred)
    resultadored=cursor.fetchall()
    lstred=[]
    lstred_frec=[]
    for nodo in resultadored:
        node1 = nodo[0]
        nodo2 = nodo[1]
        frec = nodo[2]
        #print str(node1) + '\t' + str(nodo2)
        lstred.append(str(node1) + '\t' + str(nodo2) + '\n')
        lstred_frec.append(str(node1) + '\t' + str(nodo2) + '\t' + str(frec) + '\n')


    cursor.execute(sqlnombres)
    resultadonombres=cursor.fetchall()
    lstnodosnombres=[]
    for nodo in resultadonombres:
        node = nodo[0]
        nombre = nodo[1].strip('\n')#.decode('latin-1')
        #print type(nombre), nombre
        #pais = nodo[2]
        #nic = nodo[3]
        #print str(node) + '\t' + nombre
        lstnodosnombres.append(str(node) + '\t' + nombre + '\n')


    cursor.execute(sqlpaises)
    resultadopaises=cursor.fetchall()
    lstnodospaises=[]
    for nodo in resultadopaises:
        node = nodo[0]
        pais = nodo[1]
        #print str(node) + '\t' + pais
        lstnodospaises.append(str(node) + '\t' + pais + '\n')

    cursor.close()
    conndb.close ()
    return lstred, lstnodospaises, lstnodosnombres, lstred_frec
    
def normalizar_string(unicode_string):
    u"""Retorna unicode_string sin normalizado para efectuar una búsqueda respetando mayúsculas y minúsculas.

    >>> normalizar_string(u'ñandú')
    'nandu'
    
    """
    return normalize('NFKD', unicode_string).encode('ASCII', 'ignore')

if __name__ == '__main__':
#    print findasxip('192.172.226.78')
    print findnicxas('15111')
