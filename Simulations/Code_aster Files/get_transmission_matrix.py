'''
Gets the transmission matrix in the following format:
[ P0 ]		[S00 S01 S02 S03] [v0]
[ P1 ] = 	[S10 S11 S12 S13] [v1]
[ P2 ]		[S20 S21 S22 S23] [v2]
[ P3 ]		[S30 S31 S32 S33] [v3]

Thus, each column represents the pressure results of a simulation 
Currently assumes all such <v0, v1, v2, v3> are 0 except one number 
which is non zero

Thus the produced matrix is a nice copy of the stored pressure values for each simulation
'''


import os 
import aster_processing as ap
import check_transmission_matrix as checkMatrix
import copy
import numpy as np
import cmath
import csv
import coalesce_files as coalesce

#define constants
# ARR_ZERO = np.matrix('1 0 0 0; 1 0 0 0; 1 0 0 0; 1 0 0 0')
# ARR_ONE = np.matrix('0 1 0 0; 0 1 0 0; 0 1 0 0; 0 1 0 0')
# ARR_TWO = np.matrix('0 0 1 0; 0 0 1 0; 0 0 1 0; 0 0 1 0')
# ARR_THREE = np.matrix('0 0 0 1; 0 0 0 1; 0 0 0 1; 0 0 0 1')
NUM_CYCLES = 4 #represents the number of ports
ARR_INDEX = []

ARR_ONE = [1, 0]#, 0, 0]
ARR_TWO = [0, 1]#, 1, 1]
# ARR_THREE = [0, 1, 0, 1]
# ARR_FOUR = [0, 0, 1, 1]
VELOCITY_MATRIX = [ARR_ONE, ARR_TWO]#, ARR_THREE, ARR_FOUR]

#Helper to initialize array 
def initializeArr():
	for i in range(NUM_CYCLES):
		counter = NUM_CYCLES - i
		tempArr = []
		for j in range(NUM_CYCLES**2):
			tempArr.append(1 if counter % NUM_CYCLES == 0 else 0)
			counter += 1
		ARR_INDEX.append(tempArr)
	print ARR_INDEX


#Helper function to strip the last value within a list of the next line sign
def stripEnd(line):
	line = line.strip("\n")
	return line

class updateClass(object):
	def __init__(self, numCycles, velocityMatrix):
		global NUM_CYCLES
		NUM_CYCLES = numCycles
		global VELOCITY_MATRIX
		VELOCITY_MATRIX = velocityMatrix

class transmissionMatrix(object):
	#input velocity is the vector that represents the velocity 
	def __init__(self, filename, pathToFolder, listenNode, outputfile, inputVelocity):
		initializeArr()
		self.inputVelocity = inputVelocity
		self.pathToFolder = pathToFolder
		self.dir = os.path.dirname(__file__)
		self.getListenNode(listenNode)
		self.args = self.loadFilenames(filename)
		self.getAster()
		# self.writeOutput(outputfile)


	#from the filename path, load all of the filenames that will need to be read into a list
	def loadFilenames(self, filename):
		filePath = os.path.join(self.dir, filename)
		# print "filePath is: ", filePath
		with open(filePath) as f:
			lines = f.readlines()
			for i in range(len(lines)):
				lines[i] = stripEnd(lines[i])
		return lines

	#listenNode file has one node per a line
	#and it is delineated by spaces
	def getListenNode(self, listenNode):
		filePath = os.path.join(self.dir, self.pathToFolder, listenNode)
		self.listenNodes = []
		with open(filePath) as f:
			lines = f.readlines()
			for i in range(len(lines)):
				lines[i] = stripEnd(lines[i])
				line = lines[i].split(' ')
				# print "line is: ", line
				self.listenNodes.append(line[1])
		print self.listenNodes

	def getArgs(self, complexVal):
		return complexVal.real, complexVal.imag

	#wrapper function that is used to write files 
	def writeOutput(self, outputfile):
		for i in range(NUM_CYCLES**2):
			self.writeSingleOutput(outputfile, i)

	#helper function that writes a singular output
	def writeSingleOutput(self, outputfile, index):
		outputPath = os.path.join(self.dir, self.pathToFolder, outputfile + str(index) + ".csv")
		csvfile = open(outputPath, "w")
		fieldnames = ["Frequency", "Real", "Imaginary"]
		writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
		writer.writeheader()
		for freq in self.transmission[index]:
			tempKey = self.transmission[index][freq].keys()[0] #only one key 
			real, imag = self.getArgs(self.transmission[index][freq][tempKey])
			writer.writerow({'Frequency': freq, 'Real': real, 'Imaginary': imag})


	#Helper function to get the proper array for dot producing the proper array
	def getArr(self, parity): #lambda parity: ARR_ODD if parity % 2 == 0 else ARR_EVEN
		return ARR_INDEX[parity % NUM_CYCLES]

	#returns the transmission matrix
	def returnTransmissionMatrix(self):
		return self.transmission

	def returnListNodes(self):
		return self.listenNodes

	#loads the code_aster files from the inpus file
	#then gets the transmission matrix for each file 
	def getAster(self):
		currMatrix = [{}] * NUM_CYCLES**2
		self.transmission = {}
		for i in range(len(self.args)):
			filePath = os.path.join(self.dir, self.args[i])
			intxDict, presDict = ap.main(filePath) #gets the intensity and pressure Dict for the given file 
			#resetting the current Matrix to read in new files 
			if i % NUM_CYCLES == 0:
				print "in if:\n"
				self.transmission[i] = currMatrix
				currMatrix = [{}] * NUM_CYCLES ** 2

			currMatrix = self.getTransmissionMatrix(presDict, i, currMatrix)

		#acting as a sanity check
		# tempDict1 = currMatrix[0]
		# tempDict2 = currMatrix[12]
		# print "values are same" if cmp(tempDict1, tempDict2) == 0 else "values are different"
		self.transmission = currMatrix #stores the data structure properly in the class

	#for a given presFile, this iteratively produces the proper transmission matrix
	def getTransmissionMatrix(self, presDict, parity, currMatrix):
		dictKeys = presDict.keys()
		dictKeys.sort()
		counter = 0
		for i in range(len(dictKeys)):
			currFreq = dictKeys[i]
			currMatrix = self.createMatrix(currFreq, presDict[currFreq], parity, currMatrix)
		# print currMatrix[3], "\n\n\n"

		print "len of currMatrix is: ", len(currMatrix[0].keys()) #checking to make sure everything turns out legit
		return currMatrix

	#gets the proper values from the pressure vector, based upon the current 'parity'
	#the parity is determined by the counter, which allows us to do some silly dot product manipulations 
	def getProperVector(self, presVect, counter, currFreq):
		nodeDict = {}
		for node in presVect:
			key = node.keys()[0] #note there will only be one node 
			# print node
			if key != self.listenNodes[counter % NUM_CYCLES]:
				continue
			# nodeDict[key] = float(node[key][0])/self.inputVelocity #use this to get strictly the real or strictly the imaginary component
			nodeDict[key] = complex(float(node[key][0]), float(node[key][1]))/self.inputVelocity
		return nodeDict

	#finds the "dot product" between an array and the pressure vector
	#done in order to properly create the vector 
	def dotProduct(self, currFreq, presVect, parity, transMatrix):
		arr = self.getArr(parity)
		# print len(arr)
		tempMatrix = copy.copy(transMatrix)
		counter = 0
		for i in range(len(arr)):
			if arr[i] == 0:
				continue
			nodeDict = self.getProperVector(presVect, counter, currFreq)
			currIndex = copy.copy(tempMatrix[i]) #gets the dictionary for the current transmission matrix
			currIndex[currFreq] = nodeDict
			tempMatrix[i] = currIndex
			counter += 1
		return tempMatrix


	def createMatrix(self, currFreq, presVect, parity, transMatrix):
		return self.dotProduct(currFreq, presVect, parity, transMatrix)



def main():
	initializeArr()
	fileDirectory = "Paper/Paper Copy Actual Size"
	tempOutput = "temp"
	tm = transmissionMatrix(fileDirectory + "/paperCheck.txt", fileDirectory, "collimator listennode.txt", tempOutput, 1)
	rtm = tm.returnTransmissionMatrix()
	# print rtm
	# coalesce.runCoalesce(tempOutput, "coalesced", fileDirectory)
	# fileDirectory = "Paper/Paper Copy Actual Size"
	# tempOutput = "temp"
	# tm = transmissionMatrix("Paper/Paper Copy Actual Size/paperCheck.txt", fileDirectory + "/", "collimator listennode.txt", tempOutput, 1)
	# coalesce.runCoalesce(tempOutput, "coalesced" ,fileDirectory)
	# rtm = tm.returnTransmissionMatrix()
	# tm = transmissionMatrix("Old Files/filenames.txt", "Old Files/filenames listenNode.txt", "output", 1)




# main()

