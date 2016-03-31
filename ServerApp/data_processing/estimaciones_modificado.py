#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#
# Descripción de la función de este script:
# Condición necesaria: recibe como datos de entrada el/los archivos generados por el script conversion_salida.py
# Aquellos datos que no son necesarios como entrada para otro calculo se imprimen en el archivo de salida precedidos por el caracter #
# Como salida devuelve los valores calculados de:
# tT_S	# [useg] tiempo de transito para paquetes chicos
# tH_S	# [useg] umbral de decision para paquetes encolados chicos
# tT_L	# [useg] tiempo de transito para paquetes chicos grandes
# tH_L	# [useg] umbral de decision para paquetes encolados grandes
# porcentaje de paquetes encolados [%]
# Csim
# CAB
# CBA
# lambda_S
# lambda_L

#import scipy, pylab
import scipy
import scipy.optimize
import numpy
#import matplotlib.pyplot as plt # descomentar para graficar!
import os

# Tamaños de paquetes definidos en 'udpClientTiempos.js'
#l_S = (60+8+20)*8		# [bits] 60 Bytes datos UDP + 8 Bytes header UDP + 20 Bytes header IP = 88 bytes
l_S = (48+8+20)*8		# [bits] 48 Bytes datos UDP + 8 Bytes header UDP + 20 Bytes header IP = 75 bytes
#l_L = (4262+8+3*20)*8	# [bits] 4262 Bytes datos UDP + 8 Bytes header UDP + 3*20 Bytes header IP (3 paquetes) = 4330 bytes
l_L = (4449+8+3*20)*8	# [bits] 4449 Bytes datos UDP + 8 Bytes header UDP + 3*20 Bytes header IP (3 paquetes) = 4517 bytes

#dir_base = 'datosMedidos/'
#clientes = os.listdir(dir_base)

# Aca voy a almacenar informacion entre el archivo de datos y los calculos
# clave: file_name
# valores: [tT_S, tH_S, lambda_S, tT_L, tH_L, lambda_L, %pq_queue, Csim, M_AB, C_AB, M_BA, C_BA]
info_necesaria = {}

archivos = []	# Vector con los nombres de los archivos, NO pisar
'''for ip in clientes:
	path_dst = dir_base+ip+'/'
	casos = ['_l', '_u']        # Defino los 2 casos posibles, con carga o sin carga
	for c in casos:
		fname = path_dst+ip+c+'.txt'
		fcalc = path_dst+ip+c+'.calculos'
		if os.path.isfile(fname) == True and os.path.isfile(fcalc) == False:
 			archivos.append(fname)
		elif os.path.isfile(fname) == False:
			print 'No existe este caso:',fname
'''
 #sequence | interval[useg] | length[label] | rtt | t1[useg] | (t2-t1)[useg] | (t3-t2)[useg] | (t4-t3)[useg]
archivos.append("converted_data")
for file_name in archivos:
	# Tiempos cortos
	probes_short = []			# En este vector acumulo todos los tT de paquetes cortos para hacer el histograma
	# Tiempos largos
	probes_large = []			# En este vector acumulo todos los tT de paquetes largos para hacer el histograma
	f = open(file_name, 'r')
	leer = f.readlines()
	f.close()
	for line in leer:
		if line[0] != '#':
			aux_00 = line.split(' ')
			print aux_00
			sec_num = aux_00[0]
			interval = float(aux_00[1])
			length = aux_00[2]
			rtt = float(aux_00[4])-float(aux_00[3])
			t1 = float(aux_00[3])
			t2_t1 = float(aux_00[4])-float(aux_00[3])
			t3_t2 = float(aux_00[5])-float(aux_00[4])
			t4_t3 = float(aux_00[6])-float(aux_00[5])
			tT = t4_t3 + t2_t1		# tiempo de transito, Eq. (8) de TiX
			if length == '75':		# Se usa la etiqueta '40'; NO es el tamaño real
				probes_short.append(tT)
			elif length == '4475':		# Se usa la etiqueta '1500'; NO es el tamaño real
				probes_large.append(tT)
#print length
#print t1
#print t2_t1
#print t3_t2
#print t4_t3
#print "tT: ", tT

#06/30/13|10:27:14,449725 |75|37634414973|37459879005|37459879136|37634447605

	# Informacion para calcular el histograma
	tT_Smin = int(min(probes_short))
	tT_Smax = int(max(probes_short))
	
	delta = 250
	bines = round((tT_Smax - tT_Smin)/delta,0)		# Los bines DEBE ser un entero
	paso = round((tT_Smax - tT_Smin) / bines, 2)		# El paso real del histograma, debido al bin entero
	histo = scipy.histogram(probes_short,bins=bines)

	# Salida del histograma
	frecuencias = histo[0]
	lista_frecuencias = numpy.ndarray.tolist(frecuencias)		# lo convierto a un array para poder accederlo por indice
	tiempos = histo[1]
	lista_tiempos = numpy.ndarray.tolist(tiempos)				# lo convierto a un array para poder accederlo por indice

	# Convierto el vector de tiempos a la misma longitud que el de frecuencias, calculando el punto de acumulacion en el punto medio del intervalo
	size_lista_tiempos = len(lista_tiempos)
	vector_tiempos = []
	for x in range(0,size_lista_tiempos - 1):
		aux = lista_tiempos[x]
		x_1 = aux + paso/2
		vector_tiempos.append(x_1)

	#Entradas para hacer las estimaciones 
	t_first = vector_tiempos[0]
	P_max = max(frecuencias)
	indice_t_Pmax = lista_frecuencias.index(P_max)
	t_Pmax = vector_tiempos[indice_t_Pmax]
	desvio = max(delta,(t_Pmax - t_first))

	# Truncamiento de la información
	#limite_truncamiento = t_Pmax + 3*desvio
	limite_truncamiento = t_Pmax + desvio
	tiempos_truncados = []		# Almaceno en este vector los tiempos truncados
	for t in vector_tiempos:
		if t <= limite_truncamiento:
			tiempos_truncados.append(t)

	# Documentacion de scipy - define a gaussian fitting function where:
	# p[0] = amplitude
	# p[1] = mean
	# p[2] = sigma
	fitfunc = lambda p, x: p[0]*scipy.exp(-(x-p[1])**2/(2.0*p[2]**2))
	errfunc = lambda p, x, y: fitfunc(p,x)-y

	# guess some fit parameters
	p0 = scipy.c_[P_max, t_Pmax, desvio]
	print "p0: ",p0
	# Se hace el ajuste para diferentes cantidad de tiempos y se elije el ajuste de menor cv
	almaceno_tiempos = {}
	almaceno_cv = {}
	almaceno_estimadores = {}
	# Ajustes para diferentes series
	#rango_ajuste = range(indice_t_Pmax + 1, len(tiempos_truncados))
	rango_ajuste = range(len(tiempos_truncados) - 1, len(tiempos_truncados))
	for el in rango_ajuste:
		xcorr = vector_tiempos[0:el+1]
		ycorr = lista_frecuencias[0:len(xcorr)]
		almaceno_tiempos[el] = xcorr
	
		# fit a gaussian
		print errfunc," ",p0.copy()[0]," ",(xcorr,ycorr)
		#p1, success = scipy.optimize.leastsq(errfunc, p0.copy()[0], args=(xcorr,ycorr))
		
		#p1, success = scipy.optimize.leastsq(errfunc, [(p0.copy())[0][0],(p0.copy())[0][1]], args=(xcorr,ycorr))
		p1=p0[0]
		
		almaceno_estimadores[el] = p1
	
		amp_estimada = p1[0]
		tiempo_estimado = p1[1]
		dsv_estimado = p1[2]
	
		# Calculo coeficiente de variacion
		cv = dsv_estimado/tiempo_estimado
		if cv > 0:
			almaceno_cv[cv] = el

	# Ahora me quedo con el menor de los cv para calculos y graficos del ajuste
	indice_cv = almaceno_cv.keys()
	cv_min = min(indice_cv)
	elementos_tiempo = almaceno_cv[cv_min]

	p1 = almaceno_estimadores[elementos_tiempo]
	amp_estimada = p1[0]
	tiempo_estimado = p1[1]
	# SALIDA
	tT_S = tiempo_estimado
	#------------------------------------------
	compara = info_necesaria.has_key(file_name)
	if compara == 0:
		info_necesaria[file_name] = [tT_S]
	else:
		aux = info_necesaria[file_name]
		aux.append(tT_S)
		info_necesaria[file_name] = aux
	#------------------------------------------
		
	dsv_estimado = p1[2]
	# Calculo umbral para paquetes encolados
	umbral_S = tiempo_estimado + dsv_estimado
	# SALIDA
	tH_S = umbral_S
	#------------------------------------------
	compara = info_necesaria.has_key(file_name)
	if compara == 0:
		info_necesaria[file_name] = [tH_S]
	else:
		aux = info_necesaria[file_name]
		aux.append(tH_S)
		info_necesaria[file_name] = aux
	#------------------------------------------
	# Calculo factor lambda para sync de relojes
	# SALIDA
	lambda_S = tH_S - tT_Smin
	#------------------------------------------
	compara = info_necesaria.has_key(file_name)
	if compara == 0:
		info_necesaria[file_name] = [lambda_S]
	else:
		aux = info_necesaria[file_name]
		aux.append(lambda_S)
		info_necesaria[file_name] = aux
	#------------------------------------------

	# Datos para el ajuste
	xcorr = almaceno_tiempos[elementos_tiempo]
	ycorr = lista_frecuencias[0:len(xcorr)]
	# Datos truncados	
	xrest = vector_tiempos[len(xcorr):len(vector_tiempos)]
	yrest = lista_frecuencias[len(ycorr):len(lista_frecuencias)]

	# Calculo porcentaje paquetes encolados
	pqTotal_S = len(probes_short)
	sq_S = 0	# SI encolados
	for p in probes_short:
		if p > umbral_S:
			sq_S = sq_S + 1

	#### Para graficar el histograma: descomentar las siguientes lineas 
	# Calculo los puntos de la funcion continua de ajuste
	#arreglo = numpy.arange(t_first, limite_truncamiento, 0.01)
	#fn_est = fitfunc(p1, arreglo)

	#plt.plot(xcorr,ycorr, 'go')
	#plt.plot(xcorr,ycorr, 'g-', label='Histograma')
	#plt.plot(xrest,yrest, 'bo')
	#plt.plot(xrest,yrest, 'b-', label='Truncamiento')
	#plt.plot(arreglo, fn_est,'r-', label='Funcion de ajuste')
	#plt.ylabel('Frecuencias')
	#plt.xlabel('tiempos [us]')
	#plt.title('Modelado de tiempos minimos cortos caso: '+file_name)
	#plt.grid(True)
	#plt.legend()
	#plt.show()
	#---------------------------------------------------------------
	################################################################
	# Comienzan los cálculos para paquetes grandes (L)
	tT_Lmin = int(min(probes_large))
	tT_Lmax = int(max(probes_large))

	delta = 250
	bines = round((tT_Lmax - tT_Lmin)/delta,0)		# DEBE ser entero
	paso = (tT_Lmax - tT_Lmin) / bines
	histo = scipy.histogram(probes_large,bins=bines)

	frecuencias = histo[0]
	lista_frecuencias = numpy.ndarray.tolist(frecuencias)
	tiempos = histo[1]
	lista_tiempos = numpy.ndarray.tolist(tiempos)
	# Convierto el vector de tiempos a la misma longitud que el de frecuencias, graficando el punto de acumulacion en el punto medio del intervalo
	size_lista_tiempos = len(lista_tiempos)
	vector_tiempos = []
	for x in range(0,size_lista_tiempos - 1):
		aux = lista_tiempos[x]
		x_1 = round(aux + paso/2, 2)
		vector_tiempos.append(x_1)

	# Entradas para hacer las estimaciones
	t_first = vector_tiempos[0]
	P_max = max(frecuencias)
	indice_t_Pmax = lista_frecuencias.index(P_max)
	t_Pmax = vector_tiempos[indice_t_Pmax]
	desvio = max(delta,(t_Pmax - t_first))

	# Truncamiento
	#limite_truncamiento = t_Pmax + 3*desvio
	limite_truncamiento = t_Pmax + desvio
	tiempos_truncados = []
	for t in vector_tiempos:
	    if t <= limite_truncamiento:
	        tiempos_truncados.append(t)

	# define a gaussian fitting function where
	# p[0] = amplitude
	# p[1] = mean
	# p[2] = sigma
	fitfunc = lambda p, x: p[0]*scipy.exp(-(x-p[1])**2/(2.0*p[2]**2))
	errfunc = lambda p, x, y: fitfunc(p,x)-y
	
	# guess some fit parameters
	p0 = scipy.c_[P_max, t_Pmax, desvio]

	almaceno_tiempos = {}
	almaceno_cv = {}
	almaceno_estimadores = {}
	# Ajustes para diferentes series
	#rango_ajuste = range(indice_t_Pmax + 1, len(tiempos_truncados))
	rango_ajuste = range(len(tiempos_truncados) - 1, len(tiempos_truncados))
	for el in rango_ajuste:
	    xcorr = vector_tiempos[0:el+1]
	    ycorr = lista_frecuencias[0:len(xcorr)]
	    almaceno_tiempos[el] = xcorr
	
	    # fit a gaussian
	    #p1, success = scipy.optimize.leastsq(errfunc, p0.copy()[0], args=(xcorr,ycorr))
	    p1=p0[0]

	    almaceno_estimadores[el] = p1
	
	    amp_estimada = p1[0]
	    tiempo_estimado = p1[1]
	    dsv_estimado = p1[2]
	
	    # Calculo coeficiente de variacion
	    cv = dsv_estimado/tiempo_estimado
	    if cv > 0:
	        almaceno_cv[cv] = el

	# Ahora me quedo con el menor de los cv para calculos y graficos del ajuste
	indice_cv = almaceno_cv.keys()
	cv_min = min(indice_cv)
	elementos_tiempo = almaceno_cv[cv_min]
	
	p1 = almaceno_estimadores[elementos_tiempo]
	amp_estimada = p1[0]
	tiempo_estimado = p1[1]
	# SALIDA
	tT_L = tiempo_estimado
	#------------------------------------------
	compara = info_necesaria.has_key(file_name)
	if compara == 0:
		info_necesaria[file_name] = [tT_L]
	else:
		aux = info_necesaria[file_name]
		aux.append(tT_L)
		info_necesaria[file_name] = aux
	#------------------------------------------

	dsv_estimado = p1[2]
	# Calculo umbral para paquetes encolados
	umbral_L = tiempo_estimado + dsv_estimado
	# SALIDA
	tH_L = umbral_L
	#------------------------------------------
	compara = info_necesaria.has_key(file_name)
	if compara == 0:
		info_necesaria[file_name] = [tH_L]
	else:
		aux = info_necesaria[file_name]
		aux.append(tH_L)
		info_necesaria[file_name] = aux
	#------------------------------------------
	# Calculo factor lambda para sync de relojes
	# SALIDA
	lambda_L = tH_L - tT_Lmin
	#------------------------------------------
	compara = info_necesaria.has_key(file_name)
	if compara == 0:
		info_necesaria[file_name] = [lambda_L]
	else:
		aux = info_necesaria[file_name]
		aux.append(lambda_L)
		info_necesaria[file_name] = aux
	#------------------------------------------

	# Datos del ajuste
	xcorr = almaceno_tiempos[elementos_tiempo]
	ycorr = lista_frecuencias[0:len(xcorr)]
	# Datos truncados
	xrest = vector_tiempos[len(xcorr):len(vector_tiempos)]
	yrest = lista_frecuencias[len(ycorr):len(lista_frecuencias)]

	# Calculo porcentaje paquetes encolados
	pqTotal_L = len(probes_large)
	sq_L = 0	# SI encolados largos
	for p in probes_large:
		if p > umbral_L:
			sq_L = sq_L + 1
	pqTotales = pqTotal_S + pqTotal_L
	sq = sq_S + sq_L
	# SALIDA
	pq_queue = 100 * (float(sq)/pqTotales)
	#------------------------------------------
	compara = info_necesaria.has_key(file_name)
	if compara == 0:
		info_necesaria[file_name] = [pq_queue]
	else:
		aux = info_necesaria[file_name]
		aux.append(pq_queue)
		info_necesaria[file_name] = aux
	#------------------------------------------

	#### Para graficar el histograma: descomentar las siguientes lineas 
	## Calculo los puntos de la funcion continua de ajuste
	#arreglo = numpy.arange(t_first, limite_truncamiento, 0.01)
	#fn_est = fitfunc(p1, arreglo)

	# Para graficar el histograma
	#plt.plot(xcorr,ycorr, 'go')
	#plt.plot(xcorr,ycorr, 'g-', label='Histograma')
	#plt.plot(xrest,yrest, 'bo')
	#plt.plot(xrest,yrest, 'b-', label='Truncamiento')
	#plt.plot(arreglo, fn_est,'r-', label='Funcion de ajuste')
	#plt.ylabel('Frecuencias')
	#plt.xlabel('tiempos [us]')
	#plt.title('Modelado de tiempos minimos largos caso '+file_name)
	#plt.grid(True)
	#plt.legend()
	#plt.show()
	#---------------------------------------------------------------
	################################################################

# Calculo de la capacidad simétrica	con pares de valores t2, t1
# Csim = 2*(l_L - l_S)/(tT_L - tT_S)	eq. (14) TiX
for file_name in info_necesaria.keys():
	datos = info_necesaria[file_name]
	tT_S = datos[0]
	tT_L = datos[3]
	Csim = 2*(l_L - l_S)/(tT_L - tT_S)	# [bits]/[useg] = [Mbps]
	datos.append(Csim)
	#------------------------------------------
	info_necesaria[file_name] = datos
	#------------------------------------------
	
# Calculo de la capacidad asimetrica usando la mediana como estimador
# C = (l_L - l_S)/Mr    eq. (16) TiX
for file_name in archivos:
	datos = info_necesaria[file_name]
	tH_S = datos[1]
	tH_L = datos[4]

	t_no_encolados = []
	f = open(file_name, 'r')
	leer = f.readlines()
	f.close()
	for line in leer:
		if line[0] != '#':
			valores = line.split(' ')
			seq_num = float(valores[0])
			interval = valores[1]
			length = float(valores[2])
			rtt = valores[3]
			t1 = float(valores[4])
			t2_t1 = float(valores[5])
			t3_t2 = float(valores[6])
			t4_t3 = float(valores[7].split('\n')[0])
			tT = t4_t3 + t2_t1
			componentes = (seq_num,interval,length,rtt,t1,t2_t1,t3_t2,t4_t3)
			if length == 75.0:
				if tT < tH_S:
					t_no_encolados.append(componentes)
			elif length == 4475.0:
				if tT < tH_L:
					t_no_encolados.append(componentes)

	# Busco paquetes entre los no encolados consecutivos de diferente tamaño
	# Consecutivos: t_no_encolados[i][0] - t_no_encolados[i-1][0] = 0.5
	# Diferente tamaño:  t_no_encolados[i][2] - t_no_encolados[i-1][2] = 1460.0
	data_AB = []	# t2,t1	=> upstream
	data_BA = []	# t4,t3 => downstream
	size_t_no_encolados = len(t_no_encolados)
	for i in range(1,size_t_no_encolados):
		diff_length = t_no_encolados[i][2] - t_no_encolados[i-1][2]
		if diff_length == 4400.0:
			diff_sec = t_no_encolados[i][0] - t_no_encolados[i-1][0]
			if diff_sec == 1:
				# Sentido subida
				t2_t1_actual = t_no_encolados[i][5]
				t2_t1_anterior = t_no_encolados[i-1][5]
				tiempos_AB = t2_t1_actual - t2_t1_anterior
				data_AB.append(tiempos_AB)
				# Sentido bajada
				t4_t3_actual = t_no_encolados[i][7]
				t4_t3_anterior = t_no_encolados[i-1][7]
				tiempos_BA = t4_t3_actual - t4_t3_anterior
				data_BA.append(tiempos_BA)

	# CALCULO SENTIDO AB	
	tAB_min = min(data_AB)
	tAB_max = max(data_AB)

	# HISTOGRAMA
	delta = 250
	bines = round((tAB_max - tAB_min)/delta,0)
	paso = (tAB_max - tAB_min) / bines
	histo = scipy.histogram(data_AB,bins=bines)

	frecuencias = histo[0]
	lista_frecuencias = numpy.ndarray.tolist(frecuencias)
	tiempos = histo[1]
	lista_tiempos = numpy.ndarray.tolist(tiempos)
	# Convierto el vector de tiempos a la misma longitud que el de frecuencias, graficando el punto de acumulacion en el punto medio del intervalo
	size_lista_tiempos = len(lista_tiempos)
	vector_tiempos = []
	for x in range(0,size_lista_tiempos - 1):
		aux = lista_tiempos[x]
		x_1 = aux + paso/2
		vector_tiempos.append(x_1)
	
	## Para graficar el histograma descomentar
	#x1 = vector_tiempos
	#y1 = frecuencias
	#plt.plot(x1,y1, 'go')
	#plt.plot(x1,y1, 'g-', label='Histograma')
	#plt.ylabel('Frecuencias')
	#plt.xlabel('tiempos [us]')
	#plt.title('Histograma para tiempos encolados')
	#plt.grid(True)
	#plt.legend()
	#plt.show()

	#Estimaciones
	t_first = vector_tiempos[0]
	P_max = max(frecuencias)
	indice_t_Pmax = lista_frecuencias.index(P_max)
	t_Pmax = vector_tiempos[indice_t_Pmax]
	desvio = max(delta,(t_Pmax - t_first))

	# Truncamiento
	limite_truncamiento = t_Pmax + desvio
	tiempos_truncados = []
	for t in data_AB:
		if t <= limite_truncamiento:
			tiempos_truncados.append(t)

	# Mediana entre t_first y 2 desvios
	mediana = numpy.median(tiempos_truncados)
	# SALIDA
	M_AB = mediana
	#------------------------------------------
	compara = info_necesaria.has_key(file_name)
	if compara == 0:
		info_necesaria[file_name] = [M_AB]
	else:
		aux = info_necesaria[file_name]
		aux.append(M_AB)
		info_necesaria[file_name] = aux
	#------------------------------------------
	# SALIDA
	C_AB = (l_L - l_S) / M_AB
	#------------------------------------------
	compara = info_necesaria.has_key(file_name)
	if compara == 0:
		info_necesaria[file_name] = [C_AB]
	else:
		aux = info_necesaria[file_name]
		aux.append(C_AB)
		info_necesaria[file_name] = aux
	#------------------------------------------
	
	# CALCULO SENTIDO BA
	tBA_min = min(data_BA)
	tBA_max = max(data_BA)

	# HISTOGRAMA
	delta = 250
	bines = round((tBA_max - tBA_min)/delta,0)
	paso = (tBA_max - tBA_min) / bines
	histo = scipy.histogram(data_BA,bins=bines)

	frecuencias = histo[0]
	lista_frecuencias = numpy.ndarray.tolist(frecuencias)
	tiempos = histo[1]
	lista_tiempos = numpy.ndarray.tolist(tiempos)
	# Convierto el vector de tiempos a la misma longitud que el de frecuencias, graficando el punto de acumulacion en el punto medio del intervalo
	size_lista_tiempos = len(lista_tiempos)
	vector_tiempos = []
	for x in range(0,size_lista_tiempos - 1):
		aux = lista_tiempos[x]
		x_1 = aux + paso/2
		vector_tiempos.append(x_1)
	
	## Para graficar el histograma descomentar
	#x1 = vector_tiempos
	#y1 = frecuencias
	#plt.plot(x1,y1, 'go')
	#plt.plot(x1,y1, 'g-', label='Histograma')
	#plt.ylabel('Frecuencias')
	#plt.xlabel('tiempos [us]')
	#plt.title('Histograma para tiempos encolados')
	#plt.grid(True)
	#plt.legend()
	#plt.show()

	#Estimaciones
	t_first = vector_tiempos[0]
	P_max = max(frecuencias)
	indice_t_Pmax = lista_frecuencias.index(P_max)
	t_Pmax = vector_tiempos[indice_t_Pmax]
	desvio = max(delta,(t_Pmax - t_first))

	# Truncamiento
	limite_truncamiento = t_Pmax + desvio
	tiempos_truncados = []
	for t in data_BA:
		if t <= limite_truncamiento:
			tiempos_truncados.append(t)

	# Mediana entre t_first y 2 desvios
	mediana = numpy.median(tiempos_truncados)
	# SALIDA
	M_BA = mediana
	#------------------------------------------
	compara = info_necesaria.has_key(file_name)
	if compara == 0:
		info_necesaria[file_name] = [M_BA]
	else:
		aux = info_necesaria[file_name]
		aux.append(M_BA)
		info_necesaria[file_name] = aux
	#------------------------------------------
	# SALIDA
	C_BA = (l_L - l_S) / M_BA
	#------------------------------------------
	compara = info_necesaria.has_key(file_name)
	if compara == 0:
		info_necesaria[file_name] = [C_BA]
	else:
		aux = info_necesaria[file_name]
		aux.append(C_BA)
		info_necesaria[file_name] = aux
	#------------------------------------------

# Escribo salida
for file_name in info_necesaria.keys():
	datos = info_necesaria[file_name]
	# clave: file_name
	# valores: [tT_S, tH_S, lambda_S, tT_L, tH_L, lambda_L, %pq_queue, Csim, M_AB, C_AB, M_BA, C_BA]
	tT_S = round(datos[0], 3)
	tH_S = round(datos[1], 3)
	lambda_S = round(datos[2], 3)
	tT_L = round(datos[3], 3)
	tH_L = round(datos[4], 3)
	lambda_L = round(datos[5], 3)
	pq_queue = round(datos[6], 3)
	Csim = round(datos[7], 3)
	M_AB = round(datos[8], 3)
	C_AB = round(datos[9], 3)
	M_BA = round(datos[10], 3)
	C_BA = round(datos[11], 3)
	# Para escribir en el lugar correcto
	
	'''
	busco_caso = file_name.split('/')
	ip = busco_caso[len(busco_caso)-2]
	nombre = busco_caso[len(busco_caso)-1].split('_')[0]
	caso = busco_caso[len(busco_caso)-1].split('_')[1]
	if caso == 'l.txt':
		fsalida = nombre+'_l.calculos'
	elif caso == 'u.txt':
		fsalida = nombre+'_u.calculos'
	path_dst = dir_base+ip+'/'
	fsalida_abs = path_dst+fsalida
	if os.path.isfile(fsalida_abs) == True:
		print 'Ya existe el archivo. Verificar si ya se hicieron los calculos.'
		break
	'''
	f = open("calculos_abs", 'a')
	cadena_00 = '# tT_S = '+str(tT_S)+' useg\n'
	f.write(cadena_00)
	cadena_01 = '# tH_S = '+str(tH_S)+' useg\n'
	f.write(cadena_01)
	cadena_02 = '# tT_L = '+str(tT_L)+' useg\n'
	f.write(cadena_02)
	cadena_03 = '# tH_L = '+str(tH_L)+' useg\n'
	f.write(cadena_03)
	cadena_04 = '# Capacidad Simetrica = '+str(Csim)+' Mbps\n'
	f.write(cadena_04)
	cadena_05 = '# Porcentaje de paquetes encolados = '+str(pq_queue)+' %\n'
	f.write(cadena_05)
	cadena_06 = 'Capacidad Asimetrica (subida) = '+str(C_AB)+' Mbps\n'
	f.write(cadena_06)
	cadena_07 = 'Capacidad Asimetrica (bajada) = '+str(C_BA)+' Mbps\n'
	f.write(cadena_07)
	cadena_08 = 'Parametro lambda para sync relojes (paquetes chicos) = '+str(lambda_S)+' useg\n'
	f.write(cadena_08)
	cadena_09 = 'Parametro lambda para sync relojes (paquetes grandes) = '+str(lambda_L)+' useg\n'
	f.write(cadena_09)
	# Cierro el archivo
	f.close()
