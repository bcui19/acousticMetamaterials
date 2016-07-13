'''
Takes into account the velocity values
Use this over get_identity_matrix
Although it imports the class, it makes work easier
'''

import get_identity_matrix as gim
import get_transmission_matrix as gtm
import numpy as np

#define constants
NUM_CYCLES = 4
VELOCITY_SOLUTION_MATRIX = [complex(0,0)] * NUM_CYCLES

fileDirectory = "Paper/rightFreq fullRank"
fileNames = "paperCheck.txt"
listennode = "collimator listennode.txt"
exportFile = "Computed identity vals temp"

SIM_ONE = [1, 0, 0, 0]
SIM_TWO = [0, 17, 0, 0]
SIM_THREE = [0, 0, 1, 1]
SIM_FOUR = [0, 0, 0, 13]
VELOCITY_MATRIX = [SIM_ONE, SIM_TWO, SIM_THREE, SIM_FOUR]
VELOCITY_SOLUTION_MATRIX= [0] * NUM_CYCLES

def updateClass(numCycles, velocityMatrix):
	global NUM_CYCLES
	NUM_CYCLES = numCycles
	global VELOCITY_MATRIX
	VELOCITY_MATRIX = velocityMatrix
	global VELOCITY_SOLUTION_MATRIX
	VELOCITY_SOLUTION_MATRIX = [complex(0, 0)] * NUM_CYCLES

class independentMatrix(gim.identityTransformation):
	def getOrigMatrix(self, freq):
		arrStor = []
		for i in range(NUM_CYCLES):
			tempArr = [0]*NUM_CYCLES
			press2 = self.tm[NUM_CYCLES + i][freq]
			tempArr[0] = press2[press2.keys()[0]] #there will only be one key
			press4 = self.tm[NUM_CYCLES*3 + i][freq]
			tempArr[2] = press4[press4.keys()[0]]

			for j in [1, 3]:
				tempArr[j] = VELOCITY_MATRIX[i][j]

			arrStor.append(tempArr)
		# print "arrStor is: ", arrStor
		return arrStor

	def getVelocityMatrix(self, index, freq):
		origMatrix = self.getOrigMatrix(freq)
		solutionMatrix = VELOCITY_SOLUTION_MATRIX[:]
		for i in range(NUM_CYCLES):
			if index == 0:
				solutionMatrix[i] = VELOCITY_MATRIX[i][0]
			if index == 2:
				solutionMatrix[i] = VELOCITY_MATRIX[i][2]

		# print "Velocity Vector is: ", solutionMatrix
		# print "Orig Matrix is: ", origMatrix
		return np.linalg.solve(origMatrix, solutionMatrix)


	def getTransmission(self):
		self.identityDict = {}
		for currFreq in self.freq:
			# if currFreq == 2528.0:
				# continue
			solArr = []
			for j in [0, 2]:
				presSol = self.getPressureMatrix(j, currFreq)
				velSol = self.getVelocityMatrix(j, currFreq)
				# print "pressure Solution is: ", presSol
				# print "Velocity Solution is: ", velSol
				solArr.append(presSol)
				solArr.append(velSol)

			self.identityDict[currFreq] = solArr

	def returnTransmission(self):
		return self.identityDict

def initialize():
	tempOutput = "temp"
	tm = gtm.transmissionMatrix(fileDirectory + "/" + fileNames, fileDirectory, listennode, tempOutput, 1)
	rtm = tm.returnTransmissionMatrix()
	frequencies = rtm[0].keys()#[0:1]

	return rtm, frequencies

def main():
	transmissionMatrix, frequencies = initialize()
	# tempFreq = frequencies[0:1]
	gim.updateClass(4)
	identity = independentMatrix(transmissionMatrix, frequencies, VELOCITY_VECTOR)
	identityDict = identity.returnTransmission()
	gim.exportIdentity(identityDict, fileDirectory, exportFile)
	
# main()