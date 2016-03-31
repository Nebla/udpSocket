#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#
# Descripción del script
# SALIDAS
# Este script genera como salida 4 archivos, por cada caso de entrada: caso 'l' y caso 'u'.
# Salida 1
# utilizacionInstantaneaUpstream
# Salida 2
# utilizacionInstantaneaDownstream
# Salida 3 - salida de 4 columnas: tiempo, util, H_rs, H_wavelet
# utilizacionUpstream			<- acumulando cada una hora y luego cada 5 minutos
# parametroHurstUpstreamRs		<- acumulando cada una hora y luego cada 5 minutos
# parametroHurstUpstreamWavelet	<- acumulando cada una hora y luego cada 5 minutos
# Salida 4 - salida de 4 columnas: tiempo, util, H_rs, H_wavelet
# utilizacionDownstream				<- acumulando cada una hora y luego cada 5 minutos
# parametroHurstDownstreamRs		<- acumulando cada una hora y luego cada 5 minutos
# parametroHurstDownstreamWavelet	<- acumulando cada una hora y luego cada 5 minutos
#
# Tambien se puede visualizar la sincronizacion de relojes en caso de ser necesario
# ENTRADAS
# Debe haberse ejecutado previamente el script 'estimaciones.py'. Necesita leer los datos de entrada generados por 'conversion_salida.py'y luego de ejecutar 'estimaciones.py' los siguientes valores para cada caso:
# C_AB o CA segun ecuaciones de TiX
# C_BA o CB segun ecuaciones de TiX
# lambda_S
# lambda_L

#import pylab
import scipy
import scipy.optimize
import numpy
import matplotlib.pyplot as plt
import os
import subprocess
import time

# Tamaños de paquetes definidos en 'udpClientTiempos.js'
#l_S = (60+8+20)*8       # [bits] 60 Bytes datos UDP + 8 Bytes header UDP + 20 Bytes header IP = 88 bytes
#l_L = (4262+8+3*20)*8   # [bits] 4262 Bytes datos UDP + 8 Bytes header UDP + 3*20 Bytes header IP (3 paquetes) = 4330 bytes
l_S = (48+8+20)*8		# [bits] 48 Bytes datos UDP + 8 Bytes header UDP + 20 Bytes header IP = 75 bytes
l_L = (4449+8+3*20)*8	# [bits] 4449 Bytes datos UDP + 8 Bytes header UDP + 3*20 Bytes header IP (3 paquetes) = 4517 bytes

#dir_base = 'datosMedidos/'
#clientes = os.listdir(dir_base)

# Aca voy a almacenar informacion entre el archivo de datos y los calculos
# clave: file_name
# valores: [C_AB ó CA, C_BA ó CB, lambda_S, lambda_L]
info_necesaria = {}
# Verifico existencia de archivos y leo parametros de entrada
archivos = []   # Vector con los nombres de los archivos, NO pisar
#for ip in clientes:
#	path_dst = dir_base+ip+'/'
#	casos = ['_l', '_u']        # Defino los 2 casos posibles, con carga o sin carga
#	for c in casos:
#		fname = path_dst+ip+c+'.txt'
#		if os.path.isfile(fname) == True:
#			archivos.append(fname)
#		else:
#			print 'No existe el archivo',fname
#	for c in casos:
#		fname = path_dst+ip+c+'.calculos'
#		fname_clave = path_dst+ip+c+'.txt'
#		if os.path.isfile(fname) == True:
#			f = open(fname, 'r')
#			leer = f.readlines()
#			f.close()
#			for line in leer:
#				if line[0] != '#':
#					aux_00 = line.split('= ')
#					param = aux_00[1].split(' ')[0]
#					compara = info_necesaria.has_key(fname_clave)
#					if compara == 0:
#						info_necesaria[fname_clave] = [param]
#					else:
#						aux = info_necesaria[fname_clave]
#						aux.append(param)
#						info_necesaria[fname_clave] = aux
#		else:
#			print 'No existe el archivo',fname
#
##################################################################################################################################
# Expresiones para calculo delay del canal
# tau = 0.5*min[tT(i) - tqA - tqB - 2*l(i)/C_sim]
# tau = 0.5*min[tT(i) - tqA - tqB - l(i)/CA - l(i)/CB]		Eq. (17) TiX
##################################################################################################################################
archivos.append("log_1h_37634414107.txt")
fname_clave="log_1h_37634414107.txt"
fname="log_1h_37634414107.txt.calculos"
f = open(fname, 'r')
leer = f.readlines()
f.close()
for line in leer:
	if line[0] != '#':
		aux_00 = line.split('= ')
		param = aux_00[1].split(' ')[0]
		compara = info_necesaria.has_key(fname_clave)
		if compara == 0:
			info_necesaria[fname_clave] = [param]
		else:
			aux = info_necesaria[fname_clave]
			aux.append(param)
			info_necesaria[fname_clave] = aux
##################################################################################################################################

for file_name in archivos:
	datos_almacenados = {}
	indice_secuencias = []
	delay = []
	# Datos de capacidad para calcular los tiempos de insercion
	datos_previos = info_necesaria[file_name]
	CA = float(datos_previos[0])
	CB = float(datos_previos[1])
	#
	# Umbrales para sync de relojes
	lambda_S = float(datos_previos[2])
	lambda_L = float(datos_previos[3])
	#
	f = open(file_name, 'r')
	leer = f.readlines()
	f.close()
	for line in leer:
		if line[0] != '#':
			aux_00 = line.split(' ')
			sec_num = int(aux_00[0])
			indice_secuencias.append(sec_num)
			interval = float(aux_00[1])
			length = aux_00[2]
			rtt = float(aux_00[3])
			t1 = int(aux_00[4])
			t2_t1 = int(aux_00[5])
			t2 = t2_t1 + t1
			t3_t2 = int(aux_00[6])
			t3 = t3_t2 + t2
			t4_t3 = int(aux_00[7].split('\n')[0])
			t4 = t4_t3 + t3
			tT = t2_t1 + t4_t3					# [tT] = useg
			if length == '4475':				# etiqueta, NO es el tamaño real
				size_paquete = l_L				# [bits]
			elif length == '75':				# etiqueta, NO es el tamaño real
				size_paquete = l_S				# [bits]
			tA_ins = size_paquete/CA		# bits/Mbps = useg
			tB_ins = size_paquete/CB		# bits/Mbps = useg
			tau = 0.5*(tT - tA_ins - tB_ins)		# [tau] = useg	eq. 17
			delay.append(tau)
			valores = [sec_num, length, t1, t2, t3, t4, tT, tA_ins, tB_ins, tau]
			compara = datos_almacenados.has_key(sec_num)
			if compara == 0:
				datos_almacenados[sec_num] = valores
	tau_min = min(delay)
	tau_max = max(delay)
	tau = tau_min
	#print 'Retardo MINIMO:',tau,'useg'

	# Solo se usa para luego graficar el desfasaje entre relojes
	figura4_1 = []		# almaceno + tqA(i) + deltaPsi(i)
	figura4_2 = []		# almaceno - tqB(i) + deltaPsi(i)
	# Expresiones para calculo de los tiempos encolados
	# tqA + tqB = tT(i) - 2*tau - 2*l(i)/Csim
	# tqA + tqB = tT(i) - 2*tau - l(i)/CA - l(i)/CB		Eq. (18) TiX
	for n in indice_secuencias:
		aux_00 = datos_almacenados[n]
		t1 = aux_00[2]
		t2 = aux_00[3]
		t3 = aux_00[4]
		t4 = aux_00[5]
		tT = aux_00[6]
		tA_ins = aux_00[7]
		tB_ins = aux_00[8]
		tqA_tqB = tT - 2*tau - tA_ins - tB_ins		# [tqA_tqB] = useg	eq. 18
		#print 'tqA + tqB(',n,'):', tqA_tqB
		aux_00.append(tqA_tqB)	# valores = [sec_num, length, t1, t2, t3, t4, tT, tA_ins, tB_ins, tau, tqA_tqB]
		datos_almacenados[n] = aux_00
		# 
		# Para graficar desfasaje entre relojes
		# tqA(i) + deltaPsi(i) = t2(i) - t1(i) - l(i)/CA - tau      eq. (20) TiX
		tqA_deltaPsi = t2 - t1 - tA_ins - tau
		figura4_1.append(tqA_deltaPsi)
		# - tqB(i) + deltaPsi(i) = t3(i) - t4(i) + l(i)/CB + tau    eq. (21) TiX
		tqB_deltaPsi = t3 - t4 + tB_ins + tau
		figura4_2.append(tqB_deltaPsi)

	# Busco subconjunto v
	subset_indices = []
	for n in indice_secuencias:
		aux_00 = datos_almacenados[n]
		tqA_tqB = aux_00[10]
		# Si n es impar => paquete corto
		if n % 2 != 0:
			if tqA_tqB <= lambda_S:		# eq. 18
				subset_indices.append(n)
		# Si n es par => paquete largo
		else:
			if tqA_tqB <= lambda_L:		# eq. 18
				subset_indices.append(n)

	# COMIENZO SYNC de relojes
	# deltapsi(i) = 0.5 (t2(i) - t4(i) - t1(i) + t3(i) - tqA(i) + tqB(i) - l(i)/CA + l(i)/CB )
	# deltapsi(v) = 0.5 (t2(v) - t4(v) - t1(v) + t3(v) - l(v)/CA + l(v)/CB )		Eq. (19) TiX

	# Formato de array pares_v = [v, DeltaPsi(v)]
	Dpsi_v = {}
	deltaPsi_v = []
	pares_v = []
	for m in subset_indices:
		aux_00 = datos_almacenados[m]
		t1 = aux_00[2]
		t2 = aux_00[3]
		t3 = aux_00[4]
		t4 = aux_00[5]
		tA_ins = aux_00[7]
		tB_ins = aux_00[8]
		deltaPsi = 0.5*(t2 - t4 - t1 + t3 - tA_ins + tB_ins)
		datos = (m,deltaPsi)
		pares_v.append(datos)
		# Solo para graficar
		aux_Dpsi = round(deltaPsi/1000/1000, 3)
		deltaPsi_v.append(aux_Dpsi)
		#####
		compara = Dpsi_v.has_key(m)
		if compara == 0:
			Dpsi_v[m] = datos

	# Estimación del valor inicial si v[1] != 0
	sec_inicial_i = indice_secuencias[0]
	sec_inicial_v = pares_v[0][0]
	if sec_inicial_i != sec_inicial_v:
		aux_00 = datos_almacenados[sec_inicial_i]
		t1 = aux_00[2]
		t2 = aux_00[3]
		t3 = aux_00[4]
		t4 = aux_00[5]
		tA_ins = aux_00[7]
		tB_ins = aux_00[8]
		tqA_deltaPsi = t2 - t1 - tA_ins - tau
		tqB_deltaPsi = t3 - t4 + tB_ins + tau
		Dpsi_est = tqB_deltaPsi + (tqA_deltaPsi - tqB_deltaPsi)/2
		datos = (sec_inicial_i, Dpsi_est)
		Dpsi_v[sec_inicial_i] = datos

	# Estimación del valor final
	sec_final_i = indice_secuencias[len(indice_secuencias)-1]
	sec_final_v = pares_v[len(pares_v)-1][0]
	if sec_final_i != sec_final_v:
		aux_00 = datos_almacenados[sec_final_i]
		t1 = aux_00[2]
		t2 = aux_00[3]
		t3 = aux_00[4]
		t4 = aux_00[5]
		tA_ins = aux_00[7]
		tB_ins = aux_00[8]
		tqA_deltaPsi = t2 - t1 - tA_ins - tau
		tqB_deltaPsi = t3 - t4 + tB_ins + tau
		Dpsi_est = tqB_deltaPsi + (tqA_deltaPsi - tqB_deltaPsi)/2
		datos = (sec_final_i, Dpsi_est)
		Dpsi_v[sec_final_i] = datos

	# Interpolacion
	Dpsi_i = {}
	for s in range(0,len(indice_secuencias)):
		i = indice_secuencias[s]
		# Es una secuencia con Dpsi valido ?
		compara_00 = Dpsi_v.has_key(i)
		if compara_00 != 0:		# Valida
			aux = Dpsi_v[i]
			u = aux[0]
			Du = aux[1]
			Dpsi_i[u] = aux
		else:					# No valida
			v = i+1
			for n in range(v,len(indice_secuencias)):
				compara_01 = Dpsi_v.has_key(n)
				if compara_01 != 0:		# Punto siguiente valido
					aux = Dpsi_v[n]
					v = aux[0]
					Dv = aux[1]
					break				# salgo al encontrar punto siguiente valido
			m = (Dv - Du) / (v - u)
			b = Du - m*u
			g = b + m*i
			# Condiciones que se deben cumplir para la interpolacion
			# tqA(i) = t2(i) - t1(i) - l(i)/CA - tau - DeltaPsi(i) >= 0		eq. (22) TiX
			# tqB(i) = t4(i) - t3(i) - l(i)/CB - tau + DeltaPsi(i) >= 0		eq. (23) TiX
			aux_00 = datos_almacenados[i]
			t1 = aux_00[2]
			t2 = aux_00[3]
			t3 = aux_00[4]
			t4 = aux_00[5]
			tA_ins = aux_00[7]
			tB_ins = aux_00[8]
			tqA = t2 - t1 - tA_ins - tau - g
			tqB = t4 - t3 - tB_ins - tau + g
			if tqA > 0 and tqB > 0:
				datos = (i, g)
				Dpsi_i[i] = datos
			else:
				tqA_deltaPsi = t2 - t1 - tA_ins - tau
				tqB_deltaPsi = t3 - t4 + tB_ins + tau
				# Nueva idea: comparo con los anteriores para ver de cual esta más cerca
				sec_prev = indice_secuencias[s-1]
				Dpsi_a_comparar = Dpsi_i[sec_prev][1]
				if (abs(tqA_deltaPsi - Dpsi_a_comparar)) < (abs(tqB_deltaPsi - Dpsi_a_comparar)):
					Dpsi_est = tqA_deltaPsi
				else:
					Dpsi_est = tqB_deltaPsi
				datos = (i, Dpsi_est)
				u = i
				Du = Dpsi_est
				Dpsi_v[i] = datos
				Dpsi_i[i] = datos

	# Aca ya tengo Dpsi para todo i => lo agrego a la estructura de valores
	for i in Dpsi_i.keys():
		dpsi = Dpsi_i[i][1]
		aux_00 = datos_almacenados[i]
		aux_00.append(dpsi)  # valores = [sec_num, length, t1, t2, t3, t4, tT, tA_ins, tB_ins, tau, tqA_tqB, Dpsi]
		datos_almacenados[i] = aux_00

	## GRAFICO
	## Para graficar desfasaje entre relojes, descomentar las siguientes lineas
	#x4 = []
	#y4 = []		# Dpsi(i)
	#for i in Dpsi_i.keys():
	#	aux = Dpsi_i[i]
	#	x4.append(aux[0])
	#	y = aux[1]
	#	y4.append(y)
	#
	#pylab.xlim([0,len(indice_secuencias)])
	#x1 = indice_secuencias
	#y1 = figura4_1		# + tqA(i) + deltaPsi(i)
	#y2 = figura4_2		# - tqB(i) + deltaPsi(i)
	#plt.plot(x1,y1, 'go', label='+ tqA + DPsi')
	#plt.plot(x1,y2, 'ro', label='- tqB + DPsi')
	#plt.plot(x4,y4, 'bo', label='DPsi(i)')
	#plt.ylabel('Tiempos [useg]')
	#plt.xlabel('Secuencias')
	#plt.title('Sincronizacion de relojes')
	#plt.grid(True)
	#plt.legend()
	#plt.show()

	## Para calcular y graficar Histograma para dpsi(i) - dpsi(i-1), descomentar las siguientes lineas
	#dpsi_histo = []
	#for n in range(2,len(Dpsi_i.keys())):
	#	j = int(n)
	#	i = int(n-1)
	#	if j - i == 1:
	#		compara_00 = Dpsi_i.has_key(j)
	#		compara_01 = Dpsi_i.has_key(i)
	#		if compara_00 != 0 and compara_01 != 0:
	#			dpsi_j = Dpsi_i[j][1]
	#			dpsi_i = Dpsi_i[i][1]
	#			dpsi_diff = dpsi_j - dpsi_i
	#			dpsi_histo.append(dpsi_diff)

	#delta = 250
	#dpsi_max = max(dpsi_histo)
	#dpsi_min = min(dpsi_histo)
	#bines = round((dpsi_max - dpsi_min)/delta,0)
	#paso = round((dpsi_max - dpsi_min) / bines, 2)
	#histo = scipy.histogram(dpsi_histo, bins=bines)

	#dpsi_frecuencias = histo[0]
	#dpsi_lista_frecuencias = numpy.ndarray.tolist(dpsi_frecuencias)
	#dpsi_tiempos = histo[1]
	#dpsi_lista_tiempos = numpy.ndarray.tolist(dpsi_tiempos)
	## Convierto el vector de tiempos a la misma longitud que el de frecuencias, graficando el punto de acumulacion en el punto medio del intervalo
	#size_dpsi_lista_tiempos = len(dpsi_lista_tiempos)
	#dpsi_vector_tiempos = []
	#for x in range(0,size_dpsi_lista_tiempos - 1):
	#	aux = dpsi_lista_tiempos[x]
	#	x_1 = round(aux + paso/2, 2)
	#	dpsi_vector_tiempos.append(x_1)

	## Para graficar el histograma dpsi
	#x_10 = dpsi_vector_tiempos
	#y_10 = dpsi_frecuencias
	#plt.plot(x_10,y_10, 'go')
	#plt.plot(x_10,y_10, 'g-', label='Histograma')
	#plt.ylabel('Frecuencias')
	#plt.xlabel('tiempos [us]')
	#plt.title('Histograma Dpsi(i) - Dpsi(i-1)')
	#plt.grid(True)
	#plt.legend()
	#plt.show()

	# COMIENZO CALCULOS DE tqA y tqB para todo i
	# tqA(i) = t2(i) - t1(i) - l(i)/CA - tau - DeltaPsi(i) >= 0		eq. (22) TiX
	# tqB(i) = t4(i) - t3(i) - l(i)/CB - tau + DeltaPsi(i) >= 0		eq. (23) TiX
	data_tqA = []
	data_tqB = []
	for i in indice_secuencias:
		aux_00 = datos_almacenados[i]
		t1 = aux_00[2]
		t2 = aux_00[3]
		t3 = aux_00[4]
		t4 = aux_00[5]
		tA_ins = aux_00[7]
		tB_ins = aux_00[8]
		Dpsi = Dpsi_i[i][1]
		tqA = t2 - t1 - tA_ins - tau - Dpsi
		data_tqA.append(tqA)
		aux_00.append(tqA)  # valores = [sec_num, length, t1, t2, t3, t4, tT, tA_ins, tB_ins, tau, tqA_tqB, Dpsi, tqA]
		tqB = t4 - t3 - tB_ins - tau + Dpsi
		data_tqB.append(tqB)
		aux_00.append(tqB)  # valores = [sec_num, length, t1, t2, t3, t4, tT, tA_ins, tB_ins, tau, tqA_tqB, Dpsi, tqA, tqB]
		datos_almacenados[i] = aux_00

	# Ajuste de los tiempos de encolado
	datos_analizar = [data_tqA, data_tqB]
	for d in range(0,len(datos_analizar)):
		data_analizar = datos_analizar[d]
		# Para saber en que caso estoy
		if d == 0:
			sentido = 'up'
		elif d == 1:
			sentido = 'down'

		delta = 250
		tq_max = max(data_analizar)
		tq_min = min(data_analizar)
		bines = round((tq_max - tq_min)/delta,0)
		paso = round((tq_max - tq_min) / bines, 2)
		histo = scipy.histogram(data_analizar, bins=bines)
	
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
	
		## Para graficar el histograma
		#x_10 = vector_tiempos
		#y_10 = frecuencias
		#plt.plot(x_10,y_10, 'go')
		#plt.plot(x_10,y_10, 'g-', label='Histograma')
		#plt.ylabel('Frecuencias')
		#plt.xlabel('tiempos [us]')
		#plt.grid(True)
		#plt.title('Histograma tq'+sentido)
		#plt.legend()
		#plt.show()

		#Estimaciones
		t_first = vector_tiempos[0]
		P_max = max(frecuencias)
		indice_t_Pmax = lista_frecuencias.index(P_max)
		t_Pmax = vector_tiempos[indice_t_Pmax]
		desvio = max(delta,(t_Pmax - t_first))
		print "t_first: "+str(t_first)
		print "P_max: "+str(P_max)
		print "indice_t_Pmax: "+str(indice_t_Pmax)
		print "t_Pmax: "+str(t_Pmax)
		print "desvio: "+str(desvio)
	
		# Truncamiento
		limite_truncamiento = t_Pmax + 3*desvio
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
		rango_ajuste = range(indice_t_Pmax + 1, len(tiempos_truncados))
		for el in rango_ajuste:
			xcorr = vector_tiempos[0:el+1]
			ycorr = lista_frecuencias[0:len(xcorr)]
			almaceno_tiempos[el] = xcorr
		
			# fit a gaussian
			p1, success = scipy.optimize.leastsq(errfunc, p0.copy()[0], args=(xcorr,ycorr))
			#p1=p0[0]
			
			almaceno_estimadores[el] = p1
		
			amp_estimada = round(p1[0],3)
			tiempo_estimado = round(p1[1],3)
			dsv_estimado = round(p1[2],3)
		
			# Calculo coeficiente de variacion
			cv = round(dsv_estimado/tiempo_estimado, 4)
			if cv > 0:
				almaceno_cv[cv] = el
			#almaceno_cv[cv] = el
	
		# Ahora me quedo con el menor de los cv para calculos y graficos del ajuste
		indice_cv = almaceno_cv.keys()
		cv_min = min(indice_cv)
		elementos_tiempo = almaceno_cv[cv_min]
	
		p1 = almaceno_estimadores[elementos_tiempo]
		amp_estimada = round(p1[0],3)
		tiempo_estimado = round(p1[1],3)
		dsv_estimado = round(p1[2],3)
		print "amp_estimada: "+str(amp_estimada)
		print "tiempo_estimado: "+str(tiempo_estimado)
		print "dsv_estimado: "+str(dsv_estimado)

		## Para graficar ajuste de los tq, descomentar las siguientes lineas
		xcorr = almaceno_tiempos[elementos_tiempo]
		ycorr = lista_frecuencias[0:len(xcorr)]
		xrest = vector_tiempos[len(xcorr):len(vector_tiempos)]
		yrest = lista_frecuencias[len(ycorr):len(lista_frecuencias)]
	
		arreglo = numpy.arange(t_first, limite_truncamiento, 0.01)
		fn_est = fitfunc(p1, arreglo)
		
		x_test = xcorr
		y_test = ycorr
		plt.plot(x_test,y_test, 'go')
		plt.plot(x_test,y_test, 'g-', label='Histograma')
		plt.plot(xrest,yrest, 'bo')
		plt.plot(xrest,yrest, 'b-', label='Truncamiento')
		plt.plot(arreglo, fn_est,'r-', label='Funcion de ajuste')
		plt.ylabel('Frecuencias')
		plt.xlabel('tiempos [us]')
		plt.title('Modelado de tiempos de encolado')
		plt.grid(True)
		plt.legend()
		plt.show()

		# Calculo del umbral	
		umbral = tiempo_estimado + dsv_estimado
		print "umbral:"+str(umbral)
		# Calculo de utilizacion global contando cantidad de paquetes que superan el umbral
		util = 0
		for t in data_analizar:
			if t < umbral:
				util = util + 1
		util_global = 100 - 100*util/float(len(data_analizar))
		# SALIDA
		#------------------------------------------
		compara = info_necesaria.has_key(file_name)
		if compara == 0:
			info_necesaria[file_name] = [util_global]
		else:
			aux = info_necesaria[file_name]
			aux.append(util_global)
			info_necesaria[file_name] = aux
		#------------------------------------------
	
		# Utilización instantánea
		ventana = 60
		salto = 1
		x = 1
		tiempo = []
		label = []
		eje_y = []
		for s in range(1,len(indice_secuencias)-1,salto):
			if ventana >= len(indice_secuencias):
				break
			muestras = 0		# cantidad de muestras en la ventana de 1 minuto (puede haber secuencias que fallaron)
			m = 0				# cantidad de valores de tq que superaron el umbral
			for t in range(s,ventana+1):
				compara_00 = datos_almacenados.has_key(t)
				#print t
				if compara_00 != 0:
					muestras = muestras + 1
					# valores = [sec_num, length, t1, t2, t3, t4, tT, tA_ins, tB_ins, tau, tqA_tqB, Dpsi, tqA, tqB]
					aux_00 = datos_almacenados[t]
					marcaTiempo = round(int(aux_00[2])/(1000*1000), 0)
					if sentido == 'up':
						tq = aux_00[12]		# tqA
					elif sentido == 'down':
						tq = aux_00[13]		# tqB
					if tq > umbral:
						m = m + 1
			if muestras != 0:
				y = m/float(muestras)
				eje_y.append(y)
				tiempo.append(x)
				label.append(marcaTiempo)
			x = round(x + 1/float(60), 2)
			ventana = ventana + salto
		
		#busco_caso = file_name.split('/')
		#ip = busco_caso[len(busco_caso)-2]
		#nombre = busco_caso[len(busco_caso)-1].split('_')[0]
		#caso = busco_caso[len(busco_caso)-1].split('_')[1]
		#if caso == 'l.txt' and sentido == 'up':
		#	fsalida = nombre+'_l.utilizacionInstantaneaUpstream'
		#elif caso == 'l.txt' and sentido == 'down':
		#	fsalida = nombre+'_l.utilizacionInstantaneaDownstream'
		#elif caso == 'u.txt' and sentido == 'up':
		#	fsalida = nombre+'_u.utilizacionInstantaneaUpstream'
		#elif caso == 'u.txt' and sentido == 'down':
		#	fsalida = nombre+'_u.utilizacionInstantaneaDownstream'
		##path_dst = dir_base+ip+'/'
                nombre=file_name
		if  sentido == 'up':
			fsalida = nombre+'.utilizacionInstantaneaUpstream'
		elif sentido == 'down':
			fsalida = nombre+'.utilizacionInstantaneaDownstream'
		path_dst='./'
		fsalida_abs = path_dst+fsalida
		if os.path.isfile(fsalida_abs) == True:
			print 'Ya existe el archivo. Verificar si ya se hicieron los calculos.'
		#	break
		f = open(fsalida_abs, 'a')
		cadena = '# Utilizacion global: '+str(util_global)+' %\n'
		f.write(cadena)
		cadena = '# fecha [UnixTime] | tiempo [min] | utilizacion [0-1]\n'
		f.write(cadena)
		for n in range(0,len(tiempo)):
			y2 = str(label[n])
			x = str(tiempo[n])
			y1 = str(eje_y[n])
			cadena = y2+' '+x+' '+y1+'\n'
			f.write(cadena)
		f.close()

		## Para graficar utilizacion en ventana, descomentar las siguientes lineas
		#pylab.ylim([0,1.2])
		#plt.plot(tiempo,eje_y, 'g-', label='Utilizacion')
		#plt.ylabel('% de utilizacion')
		#plt.xlabel('tiempos [min]')
		#plt.title('Utilizacion en ventana de 1 minuto')
		#plt.grid(True)
		#plt.legend()
		#plt.show()
	
		# Utilización acumulada en una hora y luego ventana desplazada cada 5 minutos
		# Acumulado en la primer hora y luego cada 5 minutos
		tiempo = []
		eje_y = []
		#ventana = 3600
		ventana = 600
		salto = 300
		#x = 60				# primer valor de tiempo
		x = 10				# primer valor de tiempo
		label = []
		for s in range(1,len(indice_secuencias),salto):
			muestras = 0		# cantidad de muestras en la ventana de 1 minuto (puede haber secuencias que fallaron)
			m = 0				# cantidad de valores de tq que superaron el umbral
			print "    s="+str(s)
			print "		if ventana="+str(ventana)+"     len(indice_secuencias)="+str(len(indice_secuencias))
			if ventana > len(indice_secuencias):
				if len(tiempo) == 0:		# Hay menos muestras que las necesarias para una hora, se hace un solo calculo
					for u in range(1,len(indice_secuencias)):
						compara_00 = datos_almacenados.has_key(u)
						if compara_00 != 0:
							muestras = muestras + 1
							# valores = [sec_num, length, t1, t2, t3, t4, tT, tA_ins, tB_ins, tau, tqA_tqB, Dpsi, tqA, tqB]
							aux_00 = datos_almacenados[u]
							marcaTiempo = round(int(aux_00[2])/(1000*1000), 0)
							if sentido == 'up':
								tq = aux_00[12]		# tqA
							elif sentido == 'down':
								tq = aux_00[13]		# tqB
							if tq > umbral:
								m = m + 1
					if muestras != 0:
						y = m/float(muestras)
						eje_y.append(y)
						tiempo.append(x)
						label.append(marcaTiempo)
				else:						# Es el ultimo intervalo de tiempos => salgo
					break
			else:
				for t in range(s,ventana+1):
					compara_00 = datos_almacenados.has_key(t)
					if compara_00 != 0:
						muestras = muestras + 1
						# valores = [sec_num, length, t1, t2, t3, t4, tT, tA_ins, tB_ins, tau, tqA_tqB, Dpsi, tqA, tqB]
						aux_00 = datos_almacenados[t]
						marcaTiempo = round(int(aux_00[2])/(1000*1000), 0)
						if sentido == 'up':
							tq = aux_00[12]		# tqA
						elif sentido == 'down':
							tq = aux_00[13]		# tqB
						if tq > umbral:
							m = m + 1
				print "muestras="+str(muestras)+"  m="+str(m)
				if muestras != 0:		# Solo genera salida cuando existen muestras
					y = m/float(muestras)
					eje_y.append(y)
					tiempo.append(x)
					label.append(marcaTiempo)
				x = x + 5
				ventana = ventana + salto
	
		print "eje_y: "+str(eje_y)
		## Para graficar utilizacion en ventana
		#pylab.ylim([0,1.2])
		plt.ylim([0,1.2])
		plt.plot(tiempo,eje_y, 'r-', label='Utilizacion')
		plt.ylabel('% de utilizacion')
		plt.xlabel('tiempos [min]')
		plt.title('Utilizacion en ventana de 5 minutos')
		plt.grid(True)
		plt.legend()
		plt.show()
	
		# Parámetro de Hurst acumulado en una hora y luego ventana desplazada cada 5 minutos
		## Acumulado en la primer hora  y luego cada 5 minutos
		tiempo = []
		y1_rs = []
		y2_wavelet = []
		#ventana = 3600
		ventana = 600
		salto = 300
		#x = 60				# primer valor de tiempo
		x = 10				# primer valor de tiempo
		for s in range(1,len(indice_secuencias),salto):
			if ventana > len(indice_secuencias):
				if len(tiempo) == 0:		# Hay menos muestras que las necesarias para una hora, se hace un solo calculo
					for u in range(1,len(indice_secuencias)):
						compara_00 = datos_almacenados.has_key(u)
						if compara_00 != 0:
							f = open('workfile', 'a')
							# valores = [sec_num, length, t1, t2, t3, t4, tT, tA_ins, tB_ins, tau, tqA_tqB, Dpsi, tqA, tqB]
							aux_00 = datos_almacenados[u]
							if sentido == 'up':
								tq = aux_00[12]		# tqA
							elif sentido == 'down':
								tq = aux_00[13]		# tqB
							if tq > 0:
								aux = str(tq)
								f.write(aux+'\n')
							f.close()
					proc = subprocess.Popen(['/usr/bin/Rscript','calculoH.R'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					stdout, stderr = proc.communicate()
					resultados = stdout
				        print " resultados: "+str(resultados)
					if len(resultados) != 0:
						aux_01 = resultados.split('RS plot H= ')
						RS = aux_01[1].split(' \n')[0]
						y1_rs.append(round(float(RS), 3))
						aux_02 = aux_01[1].split('Wavelet H= ')
						wavelet = aux_02[1].split(' +/-')[0]
						y2_wavelet.append(round(float(wavelet), 3))
					else:
						y1_rs.append(0.5)
						y2_wavelet.append(0.5)

					if os.path.isfile('workfile') == True:
						os.remove('workfile')
					tiempo.append(x)
				else:						# Es el ultimo intervalo de tiempos => salgo
					break
			else:
				for t in range(s,ventana+1):
					compara_00 = datos_almacenados.has_key(t)
					if compara_00 != 0:
						f = open('workfile', 'a')
						# valores = [sec_num, length, t1, t2, t3, t4, tT, tA_ins, tB_ins, tau, tqA_tqB, Dpsi, tqA, tqB]
						aux_00 = datos_almacenados[t]
						if sentido == 'up':
							tq = aux_00[12]		# tqA
						elif sentido == 'down':
							tq = aux_00[13]		# tqB
						if tq > 0:
							aux = str(tq)
							f.write(aux+'\n')
						f.close()
				proc = subprocess.Popen(['/usr/bin/Rscript','calculoH.R'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				stdout, stderr = proc.communicate()
				resultados = stdout
				print " resultados: "+str(resultados)
				if len(resultados) != 0:
					aux_01 = resultados.split('RS plot H= ')
					RS = aux_01[1].split(' \n')[0]
					y1_rs.append(round(float(RS), 3))
					aux_02 = aux_01[1].split('Wavelet H= ')
					wavelet = aux_02[1].split(' +/-')[0]
					y2_wavelet.append(round(float(wavelet), 3))
				else:
					y1_rs.append(0.5)
					y2_wavelet.append(0.5)
				
				if os.path.isfile('workfile') == True:
					os.remove('workfile')
				tiempo.append(x)
				x = x + 5
				ventana = ventana + salto
		
		## Para graficar parametro de Hurst en ventana
		#plt.plot(tiempo,y1_rs, 'r-', label='RS')
		#plt.plot(tiempo,y2_wavelet, 'b-', label='Wavelet')
		#plt.ylabel('Parametro de Hurst')
		#plt.xlabel('tiempos [min]')
		#plt.title('Parametro de Hurst en ventana de 5 minutos')
		#plt.grid(True)
		#plt.legend()
		#plt.show()

		#busco_caso = file_name.split('/')
		#ip = busco_caso[len(busco_caso)-2]
		#nombre = busco_caso[len(busco_caso)-1].split('_')[0]
		#caso = busco_caso[len(busco_caso)-1].split('_')[1]
		#if caso == 'l.txt' and sentido == 'up':
		#	fsalida = nombre+'_l.utilizacionHurstUpstream'
		#elif caso == 'l.txt' and sentido == 'down':
		#	fsalida = nombre+'_l.utilizacionHurstDownstream'
		#elif caso == 'u.txt' and sentido == 'up':
		#	fsalida = nombre+'_u.utilizacionHurstUpstream'
		#elif caso == 'u.txt' and sentido == 'down':
		#	fsalida = nombre+'_u.utilizacionHurstDownstream'
		#path_dst = dir_base+ip+'/'
		nombre=file_name
		if  sentido == 'up':
			fsalida = nombre+'.utilizacionHurstUpstream'
		elif sentido == 'down':
			fsalida = nombre+'.utilizacionHurstDownstream'
		path_dst='./'
		fsalida_abs = path_dst+fsalida
		if os.path.isfile(fsalida_abs) == True:
			print 'Ya existe el archivo. Verificar si ya se hicieron los calculos.'
		#	break
		f = open(fsalida_abs, 'a')
		cadena = '# fecha [UnixTime] | tiempo [min] | utilizacion [0-1] | H(RS) | H(Wavelet)\n'
		f.write(cadena)
		print "len(tiempo): "+str(len(tiempo))
		print "(tiempo): "+str(tiempo)
		for n in range(0,len(tiempo)):
			x = str(tiempo[n])
			y1 = str(eje_y[n])
			y2 = str(y1_rs[n])
			y3 = str(y2_wavelet[n])
			y4 = str(label[n])
			cadena = y4+' '+x+' '+y1+' '+y2+' '+y3+'\n'
			f.write(cadena)
		f.close()
