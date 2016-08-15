'''
Assuming that we are working with a unit cell
on an infinite plane, try to derrive the transmission matrix
for the n port system
'''


massiveLinking = __import__("master linking file")
calcPrime = __import__("Independent Matrix")
import get_identity_matrix as gim
import itertools
import numpy as np
import copy
gtw = __import__("get transmission weights")

NUM_CYCLES = 4 #represents the nnumber of simulations 

ARR_ONE = [1, 0, 0, 0]
ARR_TWO = [0, 1, 0, 0]
ARR_THREE = [0, 0, 1, 0]
ARR_FOUR = [0, 0, 0, 1]
VELOCITY_MATRIX = [ARR_ONE, ARR_TWO, ARR_THREE, ARR_FOUR]
VELOCITY_VECTOR = [0] * NUM_CYCLES #Used in finding the independent matrix
NEW_VELOCITIES = [12, 13, 4, 3] #used in crossValidation -- needs to be changed to match the length of the velocity

# print VELOCITY_MATRIX

#file linked names
filepath = "Paper/Paper Copy Actual Size"#"New Dimensions/New Dimensions v1"
simulationFile = "paperCheck.txt"#"New Dimensions Check v1.txt"
listennode = "collimator listennode.txt"#"New Dimensions Listennode.txt"
TESTNO = "Paper Actual Size"#"New Dimensions Unit Cell v1"
# faceNodes = "cylinder listennode.txt" #Used to make sure the face mesh is tight enough to ensure simulation convergence 
tempOutput = "temp"
coalescedOutput_values = TESTNO + "coalesced transmission values"
identityOutput = TESTNO + "transmission prime values" #outputs transmission prime
weightsOutput = TESTNO + "calculated transmission values" #outputs the transmission matrix values 
impedanceOutput = TESTNO + "calculated impedance" #output impedance CSV

PRESSURE_INDEX = [1, 3] #indexes that are connected ports
PRESSURE_RESU = [0 , 2]
VELOCITY_INDEX = [5, 7] #indexes that are connected ports
VELOCITY_INPUT = [4, 6] #indexes for the ports that have an input velocity 
VELOCITY_RESU = [6,7] #the indexes in the right hand side that we define the velocities for 


#defining new constants when needed 
NEW_NUM_CYCLES = 2

ARR_ONE = [1 , 0]
ARR_TWO = [0 , 1]
NEW_VELOCITY_VECTOR = [0] * NEW_NUM_CYCLES
NEW_VELOCITY_MATRIX = [ARR_ONE, ARR_TWO]


#calculates the new pressure and velocity values 
class infiniteCalc:
	def __init__(self, transmissionMatrix, frequencies):
		self.frequencies = frequencies
		self.transmissionMatrix = transmissionMatrix
		self.getIdentity() #gets the identity matrix
		self.solveSystem()

	def getIdentity(self):
		self.identity = []
		for i in range(NUM_CYCLES):
			self.identity.append([complex(1,0) if i == j else complex(0,0) for j in range(NUM_CYCLES)])
		# print "Identity matrix is: ", self.identity

	def solveSystem(self):
		self.resultStor = {}
		for freq in self.frequencies:
			self.simStor = []
			for i in range(NUM_CYCLES/2):
				# print "i is: ", i
				self.generateMatrix(i, freq)
			self.resultStor[freq] = self.simStor

	def generateMatrix(self, index, freq):
		self.matrix = []
		self.matrix += self.generateTransmission(freq)
		self.matrix += self.getConstraints()
		for i in range(NUM_CYCLES/2):
			result = self.createVelocity(index, i)
			# print "result is: ", type(result)
			self.matrix.append(result)

		self.createRHS(index)
		self.result = np.linalg.solve(self.matrix, self.rhs)
		self.simStor.append(self.result)
		# self.printMatrixInfo()


	def printMatrixInfo(self):
		print "matrix is: \n"
		for i in range(NUM_CYCLES*2):
			print self.matrix[i]
		print "rhs is: ", self.rhs
		print "result is: \n"
		for i in range(len(self.result)):
			print self.result[i]

	def generateTransmission(self, freq):
		returnMatrix = []
		for i in range(NUM_CYCLES):
			resuArr = self.identity[i][:]
			resuArr.extend(self.transmissionMatrix[freq][i])
			returnMatrix.append(resuArr)
		return returnMatrix

	def pressureConstraints(self):
		return [0 if i not in PRESSURE_INDEX else 1 if(i == 1) else -1 for i in range(NUM_CYCLES*2)]

	def velocityConstraints(self):
		return [0 if i not in VELOCITY_INDEX else 1 for i in range(NUM_CYCLES*2)]

	def getConstraints(self):
		returnList = []
		returnList.append(self.pressureConstraints())
		returnList.append(self.velocityConstraints())
		return returnList

	#creates the last two rows of the matrix
	#represents the 
	def createVelocity(self, index, currIndex):
		return [0 if i != VELOCITY_INPUT[currIndex] else 1 for i in range(NUM_CYCLES*2)]

	def createRHS(self, index):
		self.rhs = [0 if i != VELOCITY_RESU[index] else 1 for i in range(NUM_CYCLES*2)]

	def returnResult(self):
		return self.resultStor

class calculateTransmissionMatrix:
	def __init__(self, infiniteResult, frequencies):
		self.infiniteResult = infiniteResult
		self.frequencies = [44.0]
		self.extractVals()
		gtw.updateClass(NEW_NUM_CYCLES, NEW_VELOCITY_MATRIX)
		# print self.tm
		
		tw = gtw.getTransmissionWeights(self.tm)
		rtw = tw.returnWeights()

		calcPrime.updateClass(NEW_NUM_CYCLES, NEW_VELOCITY_MATRIX)
		gim.updateClass(NEW_NUM_CYCLES)
		tPrime = calcPrime.independentMatrix(self.tm, self.frequencies, NEW_VELOCITY_VECTOR)

		self.tPrime = tPrime.returnTransmission()
		print self.tPrime


	def extractVals(self):
		# print "self.infiniteResult is: ", self.infiniteResult

		self.tm = [{}] * NUM_CYCLES
		for i in range(NUM_CYCLES/2):
			for j in range(len(PRESSURE_RESU)):
				currDict = copy.copy(self.tm[2*i + j])

				for freq in self.frequencies:
					currArr = self.infiniteResult[freq][i]
					nodeDict = {'node' : currArr[PRESSURE_RESU[j]]}
					currDict[freq] = nodeDict

				self.tm[2*i+j] = currDict


if __name__ == "__main__":
	massiveLinking.updateSelf(numCycles = NUM_CYCLES, velocityMatrix = VELOCITY_MATRIX, newVelocities = NEW_VELOCITIES)
	massiveLinking.updateFilenames(filepath, simulationFile, listennode, tempOutput, coalescedOutput_values, identityOutput, weightsOutput, impedanceOutput)
	linkedData = massiveLinking.massiveLinking()
	frequencies = linkedData.returnWeights().keys()
	rtm = linkedData.returnTransmissionMatrix()
	# print rtm[1]
	# print frequencies
	infinitePlane = infiniteCalc(linkedData.returnWeights(), frequencies)
	infiniteResult = infinitePlane.returnResult()
	calculateTransmissionMatrix(infiniteResult, frequencies)
	# print infinitePlane.returnResult()[44.0][0]
	# print infinitePlane.returnResult()[44.0][1]

	# print 0







