#!/usr/bin/env python

def resultados(hora,minu,log,umbral_utiliz,umbral_H):
	utliz_Up   = 0.2
	utliz_Down = 0.7
	H_RS_Up    = 0.5
	H_Wave_Up  = 0.55
	H_RS_Down  = 0.65
	H_Wave_Down= 0.7
	return(utliz_Up,H_RS_Up,H_Wave_Up,utliz_Down,H_RS_Down,H_Wave_Down)


if __name__ == "__main__":
        if len(sys.argv) < 2:
        	print "usage: python <client>.py <logfile>\n"
        	sys.exit()
        log_file=sys.argv[1] # este archivo es la compilacion de 6 archivos de medición
	f = open(log_file, 'r')
	leer = f.readlines()
	f.close()
	umbral_utiliz=0.7 # leerlo de un archivo de configuracion
	umbral_H=0.65     # leerlo de un archivo de configuracion
        hora=18           # le pasa la hora de la medicion
        minu=10           # le pasa los minutos de la medicion
        resultados(hora,minu,leer,umbral_utiliz,umbral_H)
	# agregar acá el código para escribir la base de datos
