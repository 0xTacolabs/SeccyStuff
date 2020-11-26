"""Second attempt at writing a javascript de-obfuscator in python

Still doesn't work great, very much a work-in-progress. 

Assumes that encoding has already been removed with cyberchef or similar, 
Instead, focuses on building a dictionary of obfuscated functions and var names. 


"""


#!/usr/bin/python

import re
import sys

filename = sys.argv[1]

file = open(filename, "r")
lines = file.readlines()

varDict = {'new':"", "this":""}


def StringisReserved(string):
	#doesn't resolve a word if it is "reserved" in javascript
	 
	badList = ["null","false","true", "split","length"]
	
	#if (len(string) == 1):
	#	return True
	
	
	if string.lower() in badList:
		return True

	try:
		int(string)
		return True
	except:
		return False



def resolveVar(line,varDict):
	#resolves words to previously defined values in the var/func dictionary
	try:
		p = re.compile(r'([\d\w\_\-]+)')
		r = p.findall(line)
		#print(line)
		#print(r)
		i = 0
		for word in r:
			#if r[i+1] == "length":
			#	pass
			if (word in varDict.keys()):
				if not StringisReserved(varDict[word]):
					#line = line.replace(word,varDict[word])
					#print("success: " + word)
					#line = re.sub("[^A-Za-z1-9\-\_]"+word+"[^A-Za-z1-9\-\_]",varDict[word],line)
					p = re.compile('[^A-Za-z1-9\-\_]('+word + ')[^A-Za-z1-9\-\_]')
					#varValue = re.escape(varValue)
					r = p.findall(line)
					if r:
						print(r)
						line = re.sub(r[0],varDict[word],line)
	except:
		pass
	#print("\n")
	return line

def getSimpleVars(line,varDict):
	#extracts simple one line variable/function assignments. 
	try:
		#p = re.compile(r'([\wa-zA-Z\_]+)\s*=\s*\'?([\;\+\(\)\'\"\ \d\w\&\.\-\_]+)\'?[;\n]$')
		p = re.compile(r'([\d\w\_]+)\s*=\s*\'?(.*)\'?;')
		r = p.findall(line)
		return r
	except:
		pass
		
def resolveMath(line):
	#resolves any math equations used to obfuscate array references
	try:
		p = re.compile(r"(\([\d\s\+\-\*]+\))")
		r = p.findall(line)
		if r:
			for math in r:
				#print(math)
				line = line.replace(math,"("+str(eval(math))+")")
				
	except:
		pass
	return line


def updateDict(line,varDict):
	#updates dictionary with values extracted in current line
	try:
		resultSet = getSimpleVars(line,varDict)
	except:
		print("No matching vars in line:  " + line)
		pass
	for pair in resultSet:
		varName = pair[0]
		varValue = pair[1]
		varValue = varValue.strip("'")
		varValue = resolveVar(varValue,varDict)
		for word in varDict.keys():
			#if i in varValue:
				#varValue = varValue.replace(i, varDict[i])
			#varValue = re.sub("'[^A-Za-z1-9\-\_]"+word+"[^A-Za-z1-9\-\_]'",varDict[word],varValue)
			p = re.compile('[^A-Za-z1-9\-\_]('+word + ')[^A-Za-z1-9\-\_]')
			#varValue = re.escape(varValue)
			r = p.findall(varValue)
			if r:
				print(r)
				varValue = re.sub(r[0],varDict[word],varValue)
			
		if (varName not in varDict.keys()):
			if not (StringisReserved(varName) or StringisReserved(varValue)):
				varDict[varName] = varValue
				print("Updated: \'" + varName + "\' with value: " + varValue)
				
		#elif(varName in varDict.keys()) and not StringisReserved(varName):
		#	varDict[varName] = varValue
			


for line in lines:
	
	if "for" not in line:
		line = resolveVar(line,varDict)
		line = resolveMath(line)
		
		updateDict(line,varDict)
	print(line,end="")
print(varDict)





