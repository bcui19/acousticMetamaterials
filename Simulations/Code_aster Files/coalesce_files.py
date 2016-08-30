#separate file that will be run to concatonate files

import os
import csv
import cmath

#define global constants
NUM_FILES = 16
PATH = 0 #initializing path 
DIR = os.path.dirname(__file__)

def updateCoalesce(numCycles):
	global NUM_FILES
	NUM_FILES = numCycles ** 2

def coalesce(filenames, path):
	returnList = []
	for i in range(len(filenames)):
		freqList = []
		tempList = []
		tempPath = os.path.join(DIR, path, filenames[i])
		csvfile = open(tempPath, "r")
		reader = csv.DictReader(csvfile)
		for row in reader:
			freqList.append(float(row["Frequency"]))
			tempList.append(complex(float(row["Real"]), float(row["Imaginary"])))
		returnList.append(tempList)
	return returnList, freqList

def generateFieldnames(fieldname):
	tempArr = ["Frequency"]
	for i in range(NUM_FILES):
		tempArr.append(fieldname + str(i) + " real")
		tempArr.append(fieldname + str(i) + " imag")
	return tempArr

#helper function for sanity check
def genFieldnames(fieldname):
	tempArr = ["Frequency"]
	for i in range(NUM_FILES):
		tempArr.append(fieldname + str(i))
	return tempArr

#manually checks the values in teh maps to make sure indexing is appropriate
def checkMapping(complexMap, dividedMap):
	divKeys = dividedMap.keys()
	for i in range(len(divKeys)):
		if divKeys[i] == "Frequency":
			continue
		tempKey = divKeys[i] + " real"
		if complexMap[tempKey] != dividedMap[divKeys[i]].real:
			print "failed at key: ", divKeys[i], " returning"
			return
		tempKey = divKeys[i] + " imag"
		if complexMap[tempKey] != dividedMap[divKeys[i]].imag:
			print "failed at key: ", divKeys[i], " returning"
			return

def createMapping(fieldnames, dataset, freqList, index):
	returnMap = {"Frequency": freqList[index]}
	checkMap = {"Frequency": freqList[index]}
	tempFieldname = genFieldnames("output")
	for j in range(len(dataset)):
		returnMap[fieldnames[j*2+1]] = dataset[j][index].real
		returnMap[fieldnames[j*2+2]] = dataset[j][index].imag
		checkMap[tempFieldname[j+1]] = dataset[j][index]
	checkMapping(returnMap, checkMap) #acts as a sanity check 
	return returnMap

def rewriteData(coalescedData, freqList, path, outputName):
	outputfile = os.path.join(DIR, path, outputName + ".csv")
	csvfile = open(outputfile, "w")
	fieldnames = generateFieldnames("output")
	# print fieldnames
	# print "len of data is: ", len(coalescedData)
	writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
	writer.writeheader()
	for i in range(len(coalescedData[0])):
		curMap = createMapping(fieldnames, coalescedData, freqList, i)
		writer.writerow(curMap)

def generateFileNames(filename):
	return [filename + str(i) + ".csv" for i in range(NUM_FILES)]

def removeFiles(filenames):
	for file in filenames:
		os.remove(os.path.join(DIR, PATH, file))

#name is the filename that is generated from the transmission matrix
#outputname is the name of the outputted file 
def runCoalesce(name, outputname, path):
	global PATH
	PATH = path
	filenames = generateFileNames(name)
	coalescedData, freqList = coalesce(filenames, PATH)
	rewriteData(coalescedData, freqList, PATH, outputname)
	removeFiles(filenames)

# curname = "acoustic collimator actual size results"
# outputname = "coalesced"

# main(curname, outputname, "Paper Copy Actual Size")
