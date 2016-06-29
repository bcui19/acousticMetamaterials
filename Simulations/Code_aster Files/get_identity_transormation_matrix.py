#coded specifically for a 4x4 matrix -- needs to be modified for other matrix sizes LOL

import os 
import copy
import numpy as np
import cmath
import csv
import coalesce_files as coalesce
import get_transmission_matrix as gtm

#define constants
NUM_CYCLES = 4
ARR_INDEX = [4, 12, 6, 14, 8, 10]


#Helper function to strip the last value within a list of the next line sign
def stripEnd(line):
	line = line.strip("\n")
	return line
	
def getArrVal(pressVal, index):
	if pressVal == 0:
		return ARR_INDEX[0 if index == 0 else 1]
	elif pressVal == 1:
		return ARR_INDEX[2 if index == 0 else 3]
	else:
		return ARR_INDEX[4 if index == 0 else 5]


class identityTranmsission(object):
	def __init__(self, transmissionMatrix, listenNodes, pathToFolder, outputfile):
		#initializing basic constants for the class
		self.dir = os.path.dirname(__file__)
		self.pathToFolder = pathToFolder
		self.outputfile = outputfile #output file name


		self.tm = transmissionMatrix #sets class variable of transmission matrix
		self.listenNodes = listenNodes
		self.resultMatrix = {}
		self.generateIdentity()


	#specifically created for easy list generation
	def getPressure(self, freq, pressVal):
		tm = self.tm #creates a local copy for ease of use
		tempList = []
		for i in range(2):
			arrVal = getArrVal(pressVal, i)
			tempNodeDict = tm[arrVal][freq]
			node = tempNodeDict.keys()[0]
			tempList.append(tempNodeDict[node])
		return tempList

	def generateFieldnames(self):
		self.fieldnames = ["Frequency"]
		tempArr = ["S11", "S13", "S31", "S33"]
		for i in range(NUM_CYCLES):
			self.fieldnames.append(tempArr[i] + " real")
			self.fieldnames.append(tempArr[i] + " imag")

	def generateDict(self, freq):
		tempDict = {"Frequency": freq}
		for i in range(len(self.fieldnames)/2):
			tempDict[self.fieldnames[2*i + 1]] = self.resultMatrix[freq][i].real
			tempDict[self.fieldnames[2*i + 2]] = self.resultMatrix[freq][i].imag
		return tempDict

	def outputData(self):
		outputPath = os.path.join(self.dir, self.pathToFolder + self.outputfile + ".csv")
		csvfile = open(outputPath, "w")
		self.generateFieldnames()
		writer = csv.DictWriter(csvfile, fieldnames = self.fieldnames)
		writer.writeheader()
		for freq in self.resultMatrix:
			complexDict = self.generateDict(freq)
			writer.writerow(complexDict)


	def generateProperMatrices(self, freq, rowBool):
		#initializing the array
		ARR_INDEX[4] = 0 if rowBool else 8
		ARR_INDEX[5] = 2 if rowBool else 10

		tempPres2 = self.getPressure(freq, 0) #gets the row for 
		tempPres4 = self.getPressure(freq, 1)
		result = self.getPressure(freq, 2)
		origMatrix = np.array([tempPres2, tempPres4])
		return result, origMatrix

	def generateIdentity(self):
		tm = self.tm #create a local copy for ease of use
		for freq in self.tm[0].keys():
			#solving for good stuff
			tempResult = []
			resultMatrix, origMatrix = self.generateProperMatrices(freq, True)
			tempResult = np.linalg.solve(origMatrix, resultMatrix)

			resultMatrix, origMatrix = self.generateProperMatrices(freq, False)
			tempResult = np.concatenate((tempResult, np.linalg.solve(origMatrix, resultMatrix)), axis = 0)

			self.resultMatrix[freq] = tempResult
		self.outputData()

		


def main():
	# initializeArr()
	fileDirectory = "Paper/rightFreq"
	tempOutput = "temp"
	tm = gtm.transmissionMatrix(fileDirectory + "/paperCheck.txt", fileDirectory + "/", "collimator listennode.txt", tempOutput, 1)
	coalesce.runCoalesce(tempOutput, "coalesced", fileDirectory)
	rtm = tm.returnTransmissionMatrix()
	listenNodes = tm.returnListNodes()
	itm = identityTranmsission(rtm, listenNodes, fileDirectory + "/", "identity output")
	# itm.test()
	# print len(rtm[0].keys())
	print "rtm index is: ", rtm[4][512.0]
	print "rtm index is: ", rtm[12][512.0]
	print "rtm index is: ", rtm[6][512.0]
	print "rtm index is: ", rtm[14][512.0]





main()

