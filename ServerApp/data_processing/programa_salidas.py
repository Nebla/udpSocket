#!/usr/bin/python

import os

def creartxt(nombre):
  archi=open('Nuevas_salidas/'+nombre+'.txt','w')
  archi.close()
  return nombre

def grabartxt(line, nombre):
  archi=open('Nuevas_salidas/'+nombre+'.txt','a')
  archi.write(line)
  archi.close()

def leertxt(arch,directorio):
  f = open(directorio+'/'+arch,'r')
  leer = f.readlines()
  f.close()
  return leer

def buscar_hora(files, hora):
  pos=0
  for i in files:
    if str(i) <= 'salida'+str(hora): # Busca el archivo mas proximo a la hora ingresada
      pos+=1
    else: 
      break
  return pos

def variable_salidas(hora,directorio):
  us=3600000000
  err=0
  files = sorted(os.listdir(directorio))
  pos = buscar_hora(files, hora*us)
  salida = []
  
  if(pos>0):
    for i in range(buscar_hora(files, (hora-1)*us), pos):
      linea = leertxt(files[i],directorio)
      salida+=linea
  else: 
    err = 1
  return (salida,err)

def main():
  hora=float(input("Ingrese hora:"))
  diretorio='Salidas'
  (salida,err) = variable_salidas(hora,directorio)
  if err==0:
    nombre_arch = creartxt('salida_'+str(hora-1)+'_a_'+str(hora))
    for line in salida:  
      grabartxt(line, nombre_arch)
  else: 
    print('HORA INVALIDA')
  
if __name__ == "__main__": main()





