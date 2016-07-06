'''
Serves as a check for numpy to make sure the solution it's spitting out
is actually a stable solution
'''


gim = __import__("Independent Matrix")
import get_transmission_matrix as gtm
import numpy as np
import copy

#define constants
NUM_CYCLES = 4
NODE_REAL = 3e-16
NODE_IMAG = 1e-5

class validateIdentityMatrix(object):
	def __init__(self, identityMatrix, transmissionMatrix, inputVelocities):
		self.im = identityMatrix
		self.tm = transmissionMatrix
		self.inputVelocities = np.array(inputVelocities)
		self.computedPressure = {}
		self.checkTransmissionMatrix()


	def checkTransmissionMatrix(self):
		for freq in self.tm[0]:
			self.checkTPrime(freq)

	#gets the "transmission matrix" for a given frequency
	#in all honesty it's just a copy of the pressure matrix
	def constructTransMatrix(self, freq):
		self.curTransmission = []
		for i in range(NUM_CYCLES):
			tempArr = [self.tm[NUM_CYCLES*i+j][freq][val] for j in range(NUM_CYCLES) for val in self.tm[NUM_CYCLES*i+j][freq]]
			self.curTransmission.append(tempArr)
		self.computedPressure[freq] = np.dot(self.inputVelocities, self.curTransmission)
		# print "computed Pressure size is: ", self.computedPressure[freq].size

	def constructArrays(self, freq, index):
		self.constructPVInit(freq, index)
		self.constructPVResult(freq, index)

	def checkResult(self):
		for i in range(len(self.calcPV)):
			if i == 1 or i == 3:
				continue
			if abs(self.calcPV[i].real - self.resuPV[i].real) > NODE_REAL:
				print "we fucked up fam"
			if abs(self.calcPV[i].imag - self.resuPV[i].imag) > NODE_IMAG:
				print "we fucked up fam"
		return 0

	def checkTPrime(self, freq):
		self.curTPrime = copy.copy(self.im[freq])

		for i in range(NUM_CYCLES):
			self.constructArrays(freq, i)
			self.calcPV = np.dot(self.curTPrime, self.curPV)
			if self.checkResult() != 0:
				print "we fucked up fam"




	#constructs teh right side that the matrix is multiplied by
	def constructPVInit(self,freq, index):
		self.curPV = [0] * NUM_CYCLES
		tempNode = self.tm[NUM_CYCLES + index][freq] #there will only be one key
		self.curPV[0] = tempNode[tempNode.keys()[0]]
		tempNode = self.tm[NUM_CYCLES*3 + index][freq]
		self.curPV[2] = tempNode[tempNode.keys()[0]]

		self.curPV[1] = complex(1,0) if index == 1 or index == 2 else complex(0,0)
		self.curPV[3] = complex(1,0) if index == 2 or index == 3 else complex(0,0)

		# print "self.curPV is: ", self.curPV, "\n\n"


	def constructPVResult(self, freq, index):
		self.resuPV = [0] * NUM_CYCLES
		tempNode = self.tm[index][freq]
		self.resuPV[0] = tempNode[tempNode.keys()[0]]
		tempNode = self.tm[NUM_CYCLES*2 + index][freq]
		self.resuPV[2] = tempNode[tempNode.keys()[0]]

		self.resuPV[1] = complex(1,0) if index == 0 else complex(0,0)
		self.resuPV[3] = complex(1,0) if index == 3 else complex(0,0)


def printMatrix(tm):
	for i in range(len(tm)):
		print tm[i][512.0]

def initialize():
	fileDirectory = "Paper/Paper Copy Actual Size"
	tempOutput = "temp"
	tm = gtm.transmissionMatrix(fileDirectory + "/paperCheck.txt", fileDirectory, "collimator listennode.txt", tempOutput, 1)
	rtm = tm.returnTransmissionMatrix()
	frequencies = rtm[0].keys()#[0:1]
	# coalesce.runCoalesce(tempOutput, "coalesced", fileDirectory)

	# temp_frequencies = x[0].keys()
	# frequencies = temp_frequencies[:]
	identity = gim.independentMatrix(rtm, frequencies)
	identityDict = identity.returnTransmission()

	return identityDict, rtm

def main():
	identityMatrix, transmissionMatrix = initialize()
	inputVelocities = [4, 3, 2, 1]
	validateIdentityMatrix(identityMatrix, transmissionMatrix, inputVelocities)

main()