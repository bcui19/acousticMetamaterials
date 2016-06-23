import os 
import aster_processing as ap
import numpy as np
#define constants
ARR_ODD = [1, 0, 1, 0]
ARR_EVEN = [1, 0, 1, 0]
NUM_CYCLES = 2


def stripEnd(line):
	line = line.strip("\n")
	return line

def getArr(parity): #lambda parity: ARR_ODD if parity % 2 == 0 else ARR_EVEN
	return ARR_ODD if parity % 2 == 0 else ARR_EVEN
	

class transmissionMatrix(object):
	def __init__(self, filename):
		self.dir = os.path.dirname(__file__)
		self.args = self.loadFilenames(filename)
		self.getAster()

	#from the filename path, load all of the filenames that will need to be read into a list
	def loadFilenames(self, filename):
		filePath = os.path.join(self.dir, filename)
		with open(filePath) as f:
			lines = f.readlines()
			for i in range(len(lines)):
				lines[i] = stripEnd(lines[i])
		return lines

	def getAster(self):
		currMatrix = [{}] * NUM_CYCLES**2
		self.transmission = {}
		for i in range(1, len(self.args)):
			filePath = os.path.join(self.dir, self.args[i])
			intxDict, presDict = ap.main(filePath) #gets the intensity and pressure Dict for the given file 

			# print presDict
			#resetting the current Matrix
			if i % NUM_CYCLES == 0:
				self.transmission[i] = currMatrix
				currMatrix = [[0]] * NUM_CYCLES ** 2

			currMatrix = self.getTransmissionMatrix(presDict, i, currMatrix)

	def getTransmissionMatrix(self, presDict, parity, currMatrix):
		dictKeys = presDict.keys()
		dictKeys.sort()

		for i in range(len(dictKeys)-1, len(dictKeys)):
			currFreq = dictKeys[i]
			self.createMatrix(currFreq, presDict[currFreq], parity, currMatrix)
			# print presDict

	def getProperVector(self, presVect, counter):
		nodeDict = {}
		for node in presVect:
			tempKeys = node.keys() #note there will be only one key
			key = tempKeys [0]
			nodeDict[key] = node[key][0 if counter == 0 else 1]
		return nodeDict

	#finds the dot product between an array and the pressure vector
	def dotProduct(self, parity, presVect, transMatrix, currFreq):
		arr = getArr(parity)
		counter = 0
		for i in range(len(arr)):
			if arr[i] == 0:
				continue
			nodeDict = self.getProperVector(presVect, counter)
			# print transMatrix
			curIndex = transMatrix[i] #gets the dictionary for the current transmission matrix
			# print curIndex
			curIndex[currFreq] = nodeDict
			transMatrix[i] = curIndex
			counter += 1
		print transMatrix


	def createMatrix(self, currFreq, presDict, parity, transMatrix):
		arr = getArr(parity)
		self.dotProduct(parity, presDict, transMatrix, currFreq)



def main():
	tm = transmissionMatrix("filenames.txt")

main()