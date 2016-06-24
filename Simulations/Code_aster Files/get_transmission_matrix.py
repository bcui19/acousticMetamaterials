import os 
import aster_processing as ap
import numpy as np
import copy


#define constants
ARR_ODD = [1, 0, 1, 0]
ARR_EVEN = [0, 1, 0, 1]
NUM_CYCLES = 2


def stripEnd(line):
	line = line.strip("\n")
	return line

def getArr(parity): #lambda parity: ARR_ODD if parity % 2 == 0 else ARR_EVEN
	return ARR_ODD if parity % 2 == 0 else ARR_EVEN
	

class transmissionMatrix(object):
	#input velocity is the vector that represents the velocity 
	def __init__(self, filename, inputVelocity):
		self.imputVelocity = inputVelocity
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

	#returns the transmission matrix
	def returnTransmissionMatrix(self):
		return self.transmission

	#loads the code_aster files from the inpus file
	#then gets the transmission matrix for each file 
	def getAster(self):
		currMatrix = [{}] * NUM_CYCLES**2
		self.transmission = {}
		# print "len of self.args is: ", len(self.args)
		for i in range(len(self.args)):
			filePath = os.path.join(self.dir, self.args[i])
			print filePath
			intxDict, presDict = ap.main(filePath) #gets the intensity and pressure Dict for the given file 

			# print presDict
			#resetting the current Matrix
			if i % NUM_CYCLES == 0:
				print "in if:\n"
				self.transmission[i] = currMatrix
				currMatrix = [{}] * NUM_CYCLES ** 2

			currMatrix = self.getTransmissionMatrix(presDict, i, currMatrix)

		tempDict1 = currMatrix[0]
		tempDict2 = currMatrix[2]
		print "yes" if cmp(tempDict1, tempDict2) == 0 else "no"
		self.transmission = currMatrix

	def getTransmissionMatrix(self, presDict, parity, currMatrix):
		dictKeys = presDict.keys()
		dictKeys.sort()
		counter = 0
		for i in range(len(dictKeys)):
			currFreq = dictKeys[i]
			currMatrix = self.createMatrix(currFreq, presDict[currFreq], parity, currMatrix)
		# print currMatrix[3], "\n\n\n"

		print "len of currMatrix is: ", len(currMatrix[3].keys())
		return currMatrix

	#gets the proper values from the pressure vector, based upon the current 'parity'
	def getProperVector(self, presVect, counter):
		nodeDict = {}
		for node in presVect:
			tempKeys = node.keys() #note there will be only one key
			key = tempKeys [0]
			nodeDict[key] = node[key][0 if counter == 0 else 1]
		return nodeDict

	#finds the dot product between an array and the pressure vector
	def dotProduct(self, currFreq, presVect, parity, transMatrix):
		arr = getArr(parity)
		tempMatrix = copy.copy(transMatrix)
		counter = 0
		for i in range(len(arr)):
			if arr[i] == 0:
				continue
			nodeDict = self.getProperVector(presVect, counter)
			currIndex = copy.copy(tempMatrix[i]) #gets the dictionary for the current transmission matrix
			currIndex[currFreq] = nodeDict
			tempMatrix[i] = currIndex
			counter += 1
		return tempMatrix


	def createMatrix(self, currFreq, presVect, parity, transMatrix):
		return self.dotProduct(currFreq, presVect, parity, transMatrix)
		# tempMatrix = self.dotProduct(currFreq, presVect, parity, transMatrix)
		# return tempMatrix



def main():
	tm = transmissionMatrix("filenames.txt", [1, 0])
	rtm = tm.returnTransmissionMatrix()
	# print rtm
main()