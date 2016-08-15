masterLink = __import__("master linking file")
import get_transmission_matrix as gtm
import numpy as np

NUM_CYCLES = 4 #represents the nnumber of simulations 

ARR_ONE = [1, 0, 0, 0]
ARR_TWO = [0, 1, 0, 0]
ARR_THREE = [0, 0, 1, 0]
ARR_FOUR = [0, 0, 0, 1]
VELOCITY_MATRIX = [ARR_ONE, ARR_TWO, ARR_THREE, ARR_FOUR]
VELOCITY_VECTOR = [0] * NUM_CYCLES #Used in finding the independent matrix
NEW_VELOCITIES = [13, 17, 3, 21] #used in crossValidation -- needs to be changed to match the length of the velocity

# print VELOCITY_MATRIX

#file linked names
filepath = "New Dimensions/Dense Mesh"
simulationFile = "New Dimensions Check v1.txt"
listennode = "New Dimensions Listennode.txt"
TESTNO = "New Dimensions lowFreq"
# faceNodes = "cylinder listennode.txt" #Used to make sure the face mesh is tight enough to ensure simulation convergence 
tempOutput = "temp"
coalescedOutput_values = TESTNO + "coalesced transmission values"
identityOutput = TESTNO + "transmission prime values" #outputs transmission prime
weightsOutput = TESTNO + "calculated transmission values" #outputs the transmission matrix values 
impedanceOutput = TESTNO + "calculated impedance" #output impedance CSV


#file properties for random checking
NEW_NUM_CYCLES = 4 #represents the new number of simulation files we need to process
NEW_VELOCITIES = [13, 24, 5, 9]
newSimulationFile = "random file check.txt"


class randomValidation:
	def __init__(self, rtm, velocities, frequencies):
		self.rtm = rtm
		self.velocities = velocities
		self.frequencies = frequencies


		#getting new data
		gtm.updateClass(NEW_NUM_CYCLES, NEW_VELOCITIES)
		self.randomTransmission = gtm.transmissionMatrix(filepath + "/" + newSimulationFile, filepath, listennode, tempOutput, 1)
		self.randomtm = self.randomTransmission.returnTransmissionMatrix()

		print self.rtm[44.0]
		#some calculations
		self.calcNewPressures()
		# self.validateData()

	def calcNewPressures(self):
		self.pressures = {freq: np.dot(self.rtm[freq], self.velocities) for freq in self.frequencies}

	def validateData(self):
		for freq in self.frequencies:
			self.getSimData(freq)
			self.getCalcData(freq)
			if self.compareData():
				continue
			raise ValueError("The values don't match")
		# self.getSimData(44.0)
		# self.getCalcData(44.0)

		print self.currArr
		print self.calcData

	def getSimData(self, freq):
		self.currArr = []
		for i in range(NUM_CYCLES):
			currVal = self.randomtm[i*NUM_CYCLES][freq]
			tempKeys = currVal.keys()
			self.currArr.append(currVal[tempKeys[0]])
		# print self.currArr

	def getCalcData(self, freq):
		self.calcData = self.pressures[freq]
		# print self.calcData

	def compareData(self):
		#numpy comparison
		if np.allclose(self.calcData, self.currArr):
			return True
		return False 




if __name__ == "__main__":
	masterLink.updateSelf(numCycles = NUM_CYCLES, velocityMatrix = VELOCITY_MATRIX, newVelocities = NEW_VELOCITIES)
	masterLink.updateFilenames(filepath, simulationFile, listennode, tempOutput, coalescedOutput_values, identityOutput, weightsOutput, impedanceOutput)
	linkedData = masterLink.massiveLinking()
	rtm = linkedData.returnWeights()
	
	randomValidation(rtm, NEW_VELOCITIES, rtm.keys())













