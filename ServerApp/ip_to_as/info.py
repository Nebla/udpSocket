#!/usr/bin/python

from funciones import findpaisxip, findasxip, findnombrexas, findnicxas, selectpaisname
from math import log

def ipdecbin(ip):
    HexBin ={"0":"0000", "1":"0001", "2":"0010", "3":"0011", "4":"0100", "5":"0101", "6":"0110", "7":"0111", "8":"1000", "9":"1001", "A":"1010", "B":"1011", "C":"1100", "D":"1101", "E":"1110", "F":"1111"};

    pri_oct, seg_oct, ter_oct, cua_oct = map(int,ip.split('.'))
    pri_oct_bin = "".join([HexBin[i] for i in '%X'%pri_oct]).lstrip('0')
    while len(pri_oct_bin) < 8: pri_oct_bin = "0" + pri_oct_bin
    seg_oct_bin = "".join([HexBin[i] for i in '%X'%seg_oct]).lstrip('0')
    while len(seg_oct_bin) < 8: seg_oct_bin = "0" + seg_oct_bin
    ter_oct_bin = "".join([HexBin[i] for i in '%X'%ter_oct]).lstrip('0')
    while len(ter_oct_bin) < 8: ter_oct_bin = "0" + ter_oct_bin
    cua_oct_bin = "".join([HexBin[i] for i in '%X'%cua_oct]).lstrip('0')
    while len(cua_oct_bin) < 8: cua_oct_bin = "0" + cua_oct_bin
    ip_bin = pri_oct_bin + seg_oct_bin + ter_oct_bin + cua_oct_bin
    return ip_bin

def pais_cliente(ip_dire):
    #nics = ['lacnic', 'ripe', 'arin', 'afrinic', 'apnic']
    octeto1, octeto2, octeto3, octeto5 = ip_dire.split('.')

    #lstpaisesxip = []
    #for nic in nics:
     #   salida = findpaisxip(nic, octeto1)
      #  if salida != False:
       #     for elemento in salida:
        #        lstpaisesxip.append(elemento)
        
    lstpaisesxip = findpaisxip(octeto1)            
    #print lstpaisesxip
    pais = 'UNKNOWN'
    if len(lstpaisesxip) > 0:
        ult_mask = 0

        for linea in lstpaisesxip:
            ipcomp, host, paiscomp = linea.split('\t')
            #print pais, ipcomp, host
            host_mask = int(round(log(int(host))/log(2)))
            net_mask = 32 - host_mask
            bin_net_mask = "1"*(net_mask) + "0"*host_mask
            #print bit_host_mask, mascara

            ipcomp_bin = ipdecbin(ipcomp)

            #ult_ipcomp = str(ipcomp_bin[:(net_mask)]) + '1' * net_mask

            ip_dire_bin = ipdecbin(ip_dire)
            #print ip_dire_bin
            
            if ip_dire_bin[:net_mask] == ipcomp_bin[:net_mask]:
                if net_mask > ult_mask:
                    pais = paiscomp            
                    ult_mask = net_mask
                            
    #                print '-----------------'
    #                print paiscomp, ipcomp, host
    #                print ip_dire_bin[:net_mask]
    #                print ipcomp_bin[:net_mask]
    #                print ip_dire_bin
    #                print ipcomp_bin
    #                print '-----------------'
    return pais
            
def as_num_cliente(ip_dire):
    if ip_dire == 'UNKNOWN':
        return 'UNKNOWN'

    octeto1, octeto2, octeto3, octeto5 = ip_dire.split('.')
    lstasxip = findasxip(octeto1)

    numas = 'UNKNOWN'
    if lstasxip != False:
        ult_mask = 0
        for linea in lstasxip:
            numascomp, ipcomp, mask = linea.split('\t')
            net_mask = int(mask)
            #print pais, ipcomp, host
            bin_net_mask = "1"*(net_mask) + "0"*(32-net_mask)
    #        print net_mask, bin_net_mask

            ipcomp_bin = ipdecbin(ipcomp)

            #ult_ipcomp = str(ipcomp_bin[:(net_mask)]) + '1' * net_mask

            ip_dire_bin = ipdecbin(ip_dire)
            #print ip_dire_bin
            
            if ip_dire_bin[:net_mask] == ipcomp_bin[:net_mask]:
                if net_mask > ult_mask:
                    numas = numascomp
                    ult_mask = net_mask
                            
    #                print '-----------------'
    #                print paiscomp, ipcomp, host
    #                print ip_dire_bin[:net_mask]
    #                print ipcomp_bin[:net_mask]
    #                print ip_dire_bin
    #                print ipcomp_bin
    #                print '-----------------'
    return numas

def nombre_as(num_as):
    if num_as == 'UNKNOWN':
        return 'UNKNOWN'
    else:
        return findnombrexas(num_as)
   
def nic_as(num_as):
    if num_as == 'UNKNOWN':
        return 'UNKNOWN'
    else:
        return findnicxas(num_as)    

def pais_num_name_nic(ip_dire, idioma):
    '''
    ip_dire: direccion ipv4
    idioma: ES (spanish), EN (english)
    retorna el nombre del pais (en idioma seleccionado), numero de as y 
    el nombre del as, al que pertenece la ip 
    '''
    if idioma == 'EN':
        num_as = 'UNKNOWN'  
        namepais = 'UNKNOWN'    
        nameas = 'UNKNOWN'
        nicas = 'UNKNOWN'
    elif idioma == 'ES':
        num_as = 'DESCONOCIDO'  
        namepais = 'DESCONOCIDO'    
        nameas = 'DESCONOCIDO'
        nicas = 'DESCONOCIDO'

    octetos=ip_dire.split('.')
    if (octetos[0]=='10') or (octetos[0]=='192' and octetos[1]=='168') or (octetos[0]=='172' and '16' <= octetos[1] <= '31') or (octetos[0]=='127'):
        return num_as, namepais, nameas, nicas

    if idioma == 'EN' or idioma == 'ES':
        idioma = 'lang' + idioma
        if ip_dire != 'UNKNOWN':
            pais = pais_cliente(ip_dire)
            num_as = as_num_cliente(ip_dire)
        if num_as != 'UNKNOWN':
            nameas = nombre_as(num_as)
            nic = nic_as(num_as)
        if pais != 'UNKNOWN':
            namepais = selectpaisname(pais, idioma)
    else:
        return False

    return num_as, nameas, namepais, nic
    
    


if __name__ == '__main__':
    import sys
    ip = sys.argv[1]
    print pais_num_name_nic(ip, 'EN' )[1]


        
    





