'''
Looks at both transmission matrices 
and given a new set of velocities
determines if the solution given by numpy is valid
by checking if the values for both transmission matricies match 
'''
import get_transmission_matrix as gtm
import numpy as np
gim = __import__("Independent Matrix")
gtw = __import__("get transmission weights")



#define file constants
filepath = "Paper/Paper Copy independent"#"Paper/rightFreq independent"
simulationFile = "paperCheck.txt"
listenFile = "collimator listennode.txt"
tempOutput = "temp"

#define numerical constants
NUM_CYCLES = 4
VELOCITIES = [200, 53, 197, 1001]
NODE_REAL = 3e-4
NODE_IMAG = 1e-5


SIM_ONE = [1, 0, 0, 0]
SIM_TWO = [0, 1, 1, 1]
SIM_THREE = [0, 1, 0, 1]
SIM_FOUR = [0, 0, 1, 1]
VELOCITY_MATRIX = [SIM_ONE, SIM_TWO, SIM_THREE, SIM_FOUR]

def updateClass(numCylces, velocityMatrix, newVelocities):
	global NUM_CYCLES
	global VELOCITY_MATRIX, VELOCITIES
	NUM_CYCLES = numCylces
	VELOCITY_MATRIX = velocityMatrix
	VELOCITIES = newVelocities
	print "NUM_CYCLES is: ", NUM_CYCLES
	print "Velocities is: ", VELOCITIES

class crossValidation(object):
	def __init__(self, transmissionWeights, transmissionPrime, newVelocities):
		self.tw = transmissionWeights
		self.tp = transmissionPrime
		self.frequencies = self.tw.keys()
		self.velocities = newVelocities

		self.validate()

	def validate(self):
		for freq in self.frequencies:
			self.singleValidation(freq)

	def singleValidation(self, freq):
		self.generatePressure(freq)
		self.validatePressure(freq)

	#from the initial transmission matrix, given the new velocities
	#calculate the resultant pressures
	def generatePressure(self, freq):
		self.curPressure = np.dot(self.tw[freq], self.velocities)

	#validate that the calculated new pressures are correct
	def validatePressure(self, freq):
		self.generatePV()
		# print "curr self.tp is: ", self.tp[freq] 
		# print "curr self.curPV is: ", self.curPV
		self.calcPV = np.dot(self.tp[freq], self.curPV)
		self.checkPV()

	def generatePV(self):
		self.generatePV_Init()
		self.generatePV_Resu()

	def checkPV(self):
		for index in range(len(self.resuPV)):
			if (self.checkReal(index) != 0):
				print "we dun goof"
				# continue
			if (self.checkImag(index) != 0):
				print "we also dun goof"
			# 	continue
		# print "nothing seems wrong" #does a check, and if it doesn't hit this then we're good 

	def checkReal(self, index):
		# print "self.resuPV[index] is: ", self.resuPV[index]
		# print "self.curPressure is: ", self.curPressure
		# print "self.curPressure size is: ", self.curPressure.size
		if abs(self.resuPV[index].real - self.calcPV[index].real) > NODE_REAL:
			print "Real failure"
			print "Index is: ", index
			print "self.resuPV is: ", self.resuPV[index].real
			print "self.calcPV is: ", self.calcPV[index].real
			print "dif is: ", abs(self.resuPV[index].real - self.calcPV[index].real)
			return -1
		return 0

	def checkImag(self, index):
		if abs(self.resuPV[index].imag - self.calcPV[index].imag) > NODE_IMAG:
			print "Imag failure"
			print "index is: ", index
			print "self.resuPV is: ", self.resuPV[index].imag
			print "self.calcPV is: ", self.calcPV[index].imag
			print "dif is: ", abs(self.resuPV[index].imag - self.calcPV[index].imag)
			return -1
		return 0


	#assumes the number of cycles is at least 2
	def generatePV_Resu(self):
		self.resuPV = [0] * NUM_CYCLES

		self.resuPV[0] = self.curPressure[0]
		self.resuPV[1] = self.velocities[0]

		#allows to account for indexing of the array
		if NUM_CYCLES == 4:
			self.resuPV[2] = self.curPressure[2]
			self.resuPV[3] = self.velocities[2]

	#assumes the number of cycles is at least 2 
	def generatePV_Init(self):
		self.curPV = [0] * NUM_CYCLES
		
		self.curPV[0] = self.curPressure[1]
		self.curPV[1] = self.velocities[1]

		if NUM_CYCLES == 4:
			self.curPV[2] = self.curPressure[3]
			self.curPV[3] = self.velocities[3]

def initialize():
	tm = gtm.transmissionMatrix(filepath + "/" + simulationFile, filepath, listenFile, tempOutput, 1)
	rtm = tm.returnTransmissionMatrix()
	frequencies = rtm[0].keys()

	gim.updateVelocityMatrix(VELOCITY_MATRIX)

	identity = gim.independentMatrix(rtm, frequencies)
	identityDict = identity.returnTransmission()


	weightDict = gtw.getTransmissionWeights(rtm)
	actualWeights = weightDict.returnWeights()


	return tm, actualWeights, identityDict


def main():
	tm, actualWeights, identityDict = initialize()
	crossValidation(actualWeights, identityDict, VELOCITIES)

	print 0 #used to signal end

# main()
