#!/usr/bin/env python3

import os
import sys
import re
from multiprocessing import Pool

def logger(lineToLog):

	with open("confcompare_output.log", 'a') as logfile:

		if isinstance(lineToLog, str):
			logfile.write(lineToLog+'\n')
		elif isinstance(lineToLog, list):
			for l in lineToLog:
				logfile.write(l+'\n')

def vdomEnum(firstConf, secondConf):
	
	configs = [firstConf,secondConf]
	enumeredVdomsByConf = []

	#Vdoms Enumeration
	for conf in configs:
		
		listConfiguration =[]
		
		with open(conf) as textConfiguration:
			listConfiguration = textConfiguration.read().splitlines()

		enumVdom = []
		for line in listConfiguration:

			if re.search(r"^end", line):
				break

			vdMatch = re.findall(r"^edit (\S+)", line)
			if len(vdMatch) > 0:
				enumVdom.append(vdMatch[0])
		enumeredVdomsByConf.append(enumVdom)

	return enumeredVdomsByConf


def vdomConfExtractorWorker(vdom_and_listConfiguration):
	vdstart,vdom,listConfiguration = vdom_and_listConfiguration
	vdstart=vdstart[0]
	vdom=vdom[0]
	print("[+] Processing vdom: " + vdom)

	conflen = len(listConfiguration)
	splittedVdomsConf = []

	i = vdstart
	while i < conflen:
		
		if re.search(r"^config vdom", listConfiguration[i]) and re.search(r"^edit "+vdom, listConfiguration[i+1]):
			if re.search("next", listConfiguration[i+2]):
				pass
			else:
				vdomConf = []
				continueDig = True
				while continueDig and i+2 < conflen:

					if listConfiguration[i+1] == 'end' and listConfiguration[i+2] == 'end':
						#print("endvdom")
						vdomConf.append(listConfiguration[i])
						vdomConf.append(listConfiguration[i+1])
						vdomConf.append(listConfiguration[i+2])
						continueDig = False
					else:
						vdomConf.append(listConfiguration[i])
					i+=1
				splittedVdomsConf.append([vdom,vdomConf])
				break
		i+=1
	return(splittedVdomsConf)


def vdomConfExtractor(vdoms, confFile):

	splittedVdomsConf = []
	listConfiguration =[]


	with open(confFile) as textConfiguration:
		listConfiguration = textConfiguration.read().splitlines()

	conflen = len(listConfiguration)

	g = 0
	while g < conflen:
		if re.search(r"^config global", listConfiguration[g]):
			digGlobal = True
			globalConf = []

			while digGlobal:
				if listConfiguration[g+1] == 'end' and listConfiguration[g+2] == 'end':
					globalConf.append(listConfiguration[g])
					globalConf.append(listConfiguration[g+1])
					globalConf.append(listConfiguration[g+2])
					digGlobal = False
				else:
					globalConf.append(listConfiguration[g])
					g+=1
			splittedVdomsConf.append(['global', globalConf])
			break
		g+=1
	

	excutionPool = []
	vdStart = g
	for vdom in vdoms:
		while vdStart < conflen:
			
			if re.search(r"^config vdom", listConfiguration[vdStart]) and re.search(r"^edit "+vdom, listConfiguration[vdStart+1]):
				if re.search("next", listConfiguration[vdStart+2]):
					pass
				else:
					#print("[+] Found vdom: " + vdom + " start: " + str(vdStart))
					excutionPool.append([[vdStart],[vdom],listConfiguration])
					break
			vdStart+=1

	with Pool(processes = 8) as pool:
		poolResult = pool.map(vdomConfExtractorWorker,excutionPool)
	
	#poolResult[1][0][0] --> [pool n][result n][0|1] 0->vdom name 1->conf
	#print(poolResult[1][0][0])
	#print(poolResult[1][0][1])

	for result in poolResult:
		splittedVdomsConf.append([result[0][0],result[0][1]])

	return splittedVdomsConf

def confSectionExtractor(confSection, vdomConf):

	extractedConf = []
	extract = False
	for line in vdomConf:
		if line == confSection:
			extract = True
			extractedConf.append(line)
		elif extract:
			if line == 'end':
				extract = False
				extractedConf.append(line)
				
				return extractedConf
			else:
				if re.search(r"\w+ ENC .{15,}", line):
					pass
					#extractedConf.append(line)
				else:
					extractedConf.append(line)

def deepVdomCheck(firstVdom, secondVdom):

	enumConfSections = []
	for csect in firstVdom:
		if re.search(r"^config .*", csect) and csect != 'config vdom' and csect != 'config global':
			enumConfSections.append(csect)

	diffCount = 0
	for sec in enumConfSections:
		firstVdomSection = confSectionExtractor(sec, firstVdom)
		secondVdomSection = confSectionExtractor(sec, secondVdom)

		if firstVdomSection != secondVdomSection:
			diffCount +=1
			if len(firstVdomSection) > 20:
				print("[!] differences in: " + sec)
				logger("[!] differences in: " + sec)

				logger("First Conf:")
				if firstVdomSection != None:
					logger(firstVdomSection)
				else:
					logger("conf section not existing in First config")
					print("conf section not existing in First config")
				
				logger("Second Conf:")
				if secondVdomSection != None:
					logger(secondVdomSection)
				else:
					logger("conf section not existing in Second config")
					print("conf section not existing in Second config")
			else:
				print("[!] differences in: " + sec)
				logger("[!] differences in: " + sec)

				print("First Conf:")
				logger("First Conf:")
				if firstVdomSection != None:
					for l in firstVdomSection:
						print(l)
					logger(firstVdomSection)
				else:
					logger("conf section not existing in First config")
					print("conf section not existing in First config")
				
				print("Second Conf:")
				logger("Second Conf:")
				if secondVdomSection != None:
					for l in secondVdomSection:
						print(l)
					logger(secondVdomSection)
				else:
					logger("conf section not existing in Second config")
					print("conf section not existing in Second config")

	return diffCount

def compareVdoms(vdomsFromConfigs):

	i = 0
	while i < len(vdomsFromConfigs[0]):

		for vdom in vdomsFromConfigs[1]:
			
			if vdomsFromConfigs[0][i][0] == vdom[0]:
				if vdomsFromConfigs[0][i][1] != vdom[1]:
					print("+---------------------------------------------------------------------------------------+")
					print("[*] Checking vdom: " + vdom[0])
					print("vdom len in conf 1: " + str(len(vdomsFromConfigs[0][i][1])))
					print("vdom len in conf 2: " + str(len(vdom[1])))

					logger("+---------------------------------------------------------------------------------------+")
					logger("[*] Checking vdom: " + vdom[0])
					logger("vdom len in conf 1: " + str(len(vdomsFromConfigs[0][i][1])))
					logger("vdom len in conf 2: " + str(len(vdom[1])))

					diffCount = deepVdomCheck(vdomsFromConfigs[0][i][1], vdom[1])
					reverseDiffCount = 0

					if diffCount == 0:
						reverseDiffCount = deepVdomCheck(vdom[1], vdomsFromConfigs[0][i][1])

					if diffCount == 0 and reverseDiffCount == 0:
						print("[+] No differences spotted in both ways checks for vdom: " + vdom[0])
						logger("[+] No differences spotted in both ways checks for vdom: " + vdom[0])
					elif diffCount > 0:
						print("[!] Diff spotted on conf1 > conf2 check for vdom: " + vdom[0])
						logger("[!] Diff spotted on conf1 > conf2 check for vdom: " + vdom[0])
					elif reverseDiffCount > 0:
						print("[!] Diff spotted on conf2 > conf1 check for vdom: " + vdom[0])
						logger("[!] Diff spotted on conf2 > conf1 check for vdom: " + vdom[0])

				else:
					print("+---------------------------------------------------------------------------------------+")
					print("[+] vdom: " + vdom[0] + " are the same")
					logger("+---------------------------------------------------------------------------------------+")
					logger("[+] vdom: " + vdom[0] + " are the same")
		i+=1

def main():

	if len(sys.argv) != 3:
		print("[!] invalid arguments, please run the script with 2 config files name: ./fgDeepConfCompare.py conf1.conf conf2.conf")
		quit()

	with open("confcompare_output.log", 'w') as logfile:
		logfile.write('')

	enumeredVdomsByConf = vdomEnum(sys.argv[1], sys.argv[2])

	if len(enumeredVdomsByConf[0]) == 0 and len(enumeredVdomsByConf[1]) == 0:
		print("[+] No vdoms detected")
		logger("[+] No vdoms detected")
		
		listConfiguration1 = []
		listConfiguration2 = []

		with open(sys.argv[1]) as textConfiguration1:
			listConfiguration1 = textConfiguration1.read().splitlines()

		with open(sys.argv[2]) as textConfiguration2:
			listConfiguration2 = textConfiguration2.read().splitlines()

		if listConfiguration1 != listConfiguration2:

			diffCount = 0
			reverseDiffCount = 0
			diffCount = deepVdomCheck(listConfiguration1, listConfiguration2)

			if diffCount == 0:
				reverseDiffCount = deepVdomCheck(listConfiguration2, listConfiguration1)

			if diffCount > 0:
				print("[!] Diff spotted on conf1 > conf2 check")
				logger("[!] Diff spotted on conf1 > conf2 check")
			elif reverseDiffCount > 0:
				print("[!] Diff spotted on conf2 > conf1 check")
				logger("[!] Diff spotted on conf2 > conf1 check")
			elif diffCount == 0 and reverseDiffCount == 0:
				print("[+] No differences spotted in both ways checks")
				logger("[+] No differences spotted in both ways checks")

		else:
			print("+---------------------------------------------------------------------------------------+")
			print("[+] The given configurations are the same")
			logger("+---------------------------------------------------------------------------------------+")
			logger("[+] The given configurations are the same")

	elif len(enumeredVdomsByConf[0]) > 0 and len(enumeredVdomsByConf[1]) > 0:

		extractedVdomsFromConfigs = []
		extractedVdomsFromConfigs.append(vdomConfExtractor(enumeredVdomsByConf[0], sys.argv[1]))
		extractedVdomsFromConfigs.append(vdomConfExtractor(enumeredVdomsByConf[1], sys.argv[2]))
		
		compareVdoms(extractedVdomsFromConfigs)
	else:
		print("[*] it is not possible to compare a conf with vdoms with one wihtout")
		quit()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
