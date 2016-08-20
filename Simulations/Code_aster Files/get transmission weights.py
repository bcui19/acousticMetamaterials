'''
Takes in the stored value from the simulations
and actually solves for the transmission matrix
'''

import numpy as np
import get_transmission_matrix as gtm

#define file constants
filepath = "Paper/Paper Copy independent"
simulationFile = "paperCheck.txt"
listenFile = "collimator listennode.txt"
tempOutput = "temp"

#define constants
NUM_CYCLES = 2	
ARR_ONE = [1, 0]#, 0, 0]
ARR_TWO = [0, 1]#, 1, 1]
# ARR_THREE = [0, 1, 0, 1]
# ARR_FOUR = [0, 0, 1, 1]
VELOCITY_MATRIX = [ARR_ONE, ARR_TWO]#, ARR_THREE, ARR_FOUR]

#helper used to strip the end of a list of '\n'
def stripEnd(line):
	line = line.strip("\n")
	return line

#updates the global variables used when called 
class updateClass(object):
	def __init__(self, numCylces, velocityMatrix):
		global NUM_CYCLES
		NUM_CYCLES = numCylces
		global VELOCITY_MATRIX
		VELOCITY_MATRIX = velocityMatrix

class getTransmissionWeights(object):
	def __init__(self, transmissionMatrix):
		self.tm = transmissionMatrix
		self.frequencies = self.tm[0].keys()
		self.solveMatrix()

	#solves through every frequency the given transmission matrix
	#as the transmission matrix is frequency dependent
	def solveMatrix(self):
		self.weights = {}
		for freq in self.frequencies:
			# print "freq is: ", freq
			tempArr = []
			#goes through each row of the transmission matrix
			#index represents which pressure number 
			for index in range(NUM_CYCLES):
				tempArr.append(self.computeWeights(freq, index))
			self.weights[freq] = tempArr
		# print self.weights

	def computeWeights(self, freq, index):
		self.getPressure(freq, index)
		# print np.linalg.solve(VELOCITY_MATRIX, self.pressureVector)
		return np.linalg.solve(VELOCITY_MATRIX, self.pressureVector)

	def getPressure(self, freq, index):
		self.pressureVector = []
		for i in range(NUM_CYCLES):
			tempDict = self.tm[NUM_CYCLES*index + i][freq]
			self.pressureVector.append(tempDict[tempDict.keys()[0]])

	def returnWeights(self):
		return self.weights

	def averageWeights(self):
		for freq in self.weights:
			currMatrix = self.weights[freq]
			self.averageMatrix(currMatrix, freq)

	def averageMatrix(self, currMatrix, freq):
		tempArr = [0] * NUM_CYCLES
		for i in range(NUM_CYCLES):
			# print currMatrix[i]
			for j in range(NUM_CYCLES):
				tempArr[j] += currMatrix[i][(j+i)%NUM_CYCLES]
			# print "tempArr now is: ", tempArr
		tempArr = [tempArr[i]/NUM_CYCLES for i in range(NUM_CYCLES)]
		newArr = []
		for i in range(NUM_CYCLES):
			newArr.append(tempArr[:])
		self.weights[freq] = newArr[:]
		# print "temp Arr is: ", tempArr


def main():
	tm = gtm.transmissionMatrix(filepath + "/" + simulationFile, filepath, listenFile, tempOutput, 1)
	rtm = tm.returnTransmissionMatrix()
	# update(2, VELOCITY_MATRIX)

	getTransmissionWeights(rtm)
# main()

