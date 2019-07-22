#!/usr/bin/python
# -*- coding: utf-8 -*-
#UNAM-Becarios
#Leal Gonzalez Ignacio
#Practica 2 Particiones

from sys import exit,argv
from binascii import unhexlify

def MBR(disk):
	"""
	Funcion que guarda en una estructura los primeros 512 bytes del dispositivo, dividiendola en codigo de arranque,
	tabla de particiones e identificador de fin de la estructura MBR, para guardar la estructura utilizamos un 
	diccionario.
	"""
	with open(disk, 'rb') as device:
		mbr=device.read(512)
		mbrHex=[str(hex(ord(byte)).split('x')[-1]).zfill(2) for byte in mbr]
		estructuraMBR={0:mbrHex[:446], #Codigo de arranque
				   	1:mbrHex[446:446+64], #Tabla de particiones
				   	2:mbrHex[446+64:] #Fin mbr
					}
	estructuraMBR[2]=["55","aa"] #Numero magico mbr
	return estructuraMBR

def particion(estructura):
	"""
	Funcion que define las 4 particiones en la tabla MBR
	"""
	particiones={1:estructura[:16], #Particion 1
				2:estructura[16:32], #Particion 2
				3:estructura[32:48], #Particion 3
				4:estructura[48:], #Particion 4
	}
	return particiones

def tipoParticion():
	"""
	Funcion para definir si es primaria o extendida, devolviendo el codigo del sistema de archivos y el nombre del 
	sistema de archivos
	"""
	tipo = raw_input("p primaria\ne extendida\ns salir\nSeleccione una opcion (default p): ")
	if tipo=="p":	
		particion = tParticion()
	elif tipo=="e":	
		particion="05", "Extendida"
	elif tipo=="s": 
		exit()
	elif tipo=="": 
		particion = tParticion()
	return particion

def tParticion():
	"""
	Funcion que selecciona el sistema de archivos, para la particion, devolviendo el codigo del sistema de archivos y 
	el nombre del sistema de archivos
	"""
	sArchivos={"06":"FAT16", 
				"07":"HPFS/NTFS", 
				"82":"Linux swap",
				"83":"Linux"
			}
	while True:
		print "Sistemas de archivos:"
		for i in sArchivos:	
			print i + " " + sArchivos[i]
		particion=raw_input("Selecciona el sistema de archivos a utilizar (Valor): ")
		for i in sArchivos:
			if particion==i:
				return i, sArchivos[i]

def numeroParticion():
	"""
	Funcion para seleccionar la particion a crear.
	"""
	while True:
		numPar=raw_input("Numero de particion (1-4): ")
		numPar=int(numPar)
		break
	return numPar

def size():
	"""
	Función para determinar la longitud de la particion en MB o GB, pasandolo a formato little endian 
	"""
	while True:
		unidad=raw_input("Unidad de medida M (MegaBytes), G (GigaBytes): ")
		break
	if 'M' in unidad: 
		unidad=int(unidad[:-1])*1048576
	elif 'G' in unidad: 
		unidad=int(unidad[:-1])*1073741824
	unidad=str(hex(unidad/512)).split('x')[-1].zfill(8)
	tamLE=[]
	aux=0
	for i in range(4):  # se separa por cada byte
		tamLE.append(unidad[aux:aux+2])
		aux+=2
	return tamLE[::-1]  # se invierte para tenerlo en little endian

def sector(particion, longitud, longitudAux=[]):
	"""
	Función que asigna los bytes 8-11 del sector de inicio.
	"""
	if longitudAux==[]:
		particion[8:12]=['00','08','00','00']  # partición de inicio por defecto 2048 en decimal
	else:
		particion[8:12]=map(lambda var1, var2: str(hex(int(var1,16) + int(var2,16))).split('x')[-1].zfill(2), longitud, longitudAux) 
	return particion

def numSectores(particion, longitud):
        """
	Funcion que coloca en la tabla MBR la longitud de la particion
        """
        particion[12:] = longitud
        return particion

def tipoMBR(particion, codigo):
	"""
	Función que asigna el tipo de partición a la tabla MBR.
	"""
	particion[4] = codigo
	return particion

def actMBR(numPar, particion, estructura):
        """
        Funcion que escribe en la tabla MBR los datos del numero de particion que se le pasa por argumento
	"""
        if numPar == 1: 
		inicio, fin = 0, 16
        elif numPar == 2: 
		inicio, fin = 16, 32
        elif numPar == 3: 
		inicio, fin = 32, 48
        elif numPar == 4: 
		inicio, fin = 48, 64
        estructura[inicio:fin] = particion
        return estructura

def newDisc(estructura, disk):
	"""
	Funcion para escribir en el dispositivo que se paso como argumento para ejecutar el programa la tabla MBR.
	"""
	with open(disk, 'wb') as device:
		mbrAux=""
		for i in estructura:
			for length in estructura[i]:
				if len(length)==3: 
					length=length[1:]
				mbrAux+=unhexlify(length)
		device.write(mbrAux)

if __name__ == '__main__':
	estructura=MBR(argv[1])
	particiones=particion(estructura[1])
	while True:
		codigo,saNombre=tipoParticion()
		numPar=numeroParticion()
		longitud=size()
		opcion = raw_input("Guardar (w), salir (q), regresar (Enter): ")
		if opcion == "w":
			if numPar == 1:
				particiones[numPar] = sector(particiones[numPar], longitud)
			else:
				particiones[numPar] = sector(particiones[numPar], longitud, particiones[numPar-1][8:12])
			particiones[numPar] = numSectores(particiones[numPar], longitud)
			particiones[numPar] = tipoMBR(particiones[numPar], codigo)
			estructura[1] = actMBR(numPar, particiones[numPar], estructura[1])
			newDisc(estructura, argv[1])
			print "Particion " + str(numPar) + " sistema de archivos " + saNombre
		elif opcion == "q":	
			break
