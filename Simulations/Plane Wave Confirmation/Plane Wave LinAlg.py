'''
Trying to solve the system:

Ax= b
where A is the constant value represented by e^{-kx}/r and b is the zero vector
'''

import numpy as np
import math
import itertools
import matplotlib.pyplot as plt
import copy

def calculateDetector_Midpoint():
	return NUM_DETECTORS/2

#some mathematical constants that seem somewhat useful
SPEED_OF_SOUND = 343.21 #in m/s
RHO = 1.2041 #density of air 


#define constants
NUM_PORTS = 11
NUM_DETECTORS = 20
DETECTOR_MID = calculateDetector_Midpoint()
NUM_ROWS = 10

PORT_SPACING = 0.0011375
DETECTOR_SPACING = 0.00025
ROW_SPACING = 0.05

MIDPOINT = (NUM_PORTS-1)/2.0 * PORT_SPACING

FREQ_LOW = 25000
FREQ_HIGH = 25012
FREQ_DIFF = 12

#Colors 
COLOR_ARR = []



#acts as a global update for convenience 
def globalUpdate(numRows, numPorts, numDetectors):
	global NUM_PORTS, NUM_ROWS, NUM_DETECTORS, DETECTOR_MID
	NUM_PORTS = numPorts
	NUM_ROWS = numRows
	NUM_DETECTORS = numDetectors
	DETECTOR_MID = calculateDetector_Midpoint()


def generateSourceLoc(port_NUM):
	return port_NUM * PORT_SPACING

def generateDetectorX(detectorNum):
	return MIDPOINT + (detectorNum - DETECTOR_MID+1) * DETECTOR_SPACING

def generateDetectorY(rowNum):
	return (rowNum + 1) * ROW_SPACING

class source:
	def __init__(self, location, speed):
		self.location = location
		self.speed = speed

	def returnLoc(self):
		return self.location

class detector:
	def __init__(self, xLoc, yLoc):
		self.location = (xLoc, yLoc)

	def returnLoc(self):
		return self.location


class runCalculation:
	def __init__(self):
		self.portList = [source(generateSourceLoc(i), SPEED_OF_SOUND) for i in range(NUM_PORTS)]
		self.detectorDict = {j: [detector(generateDetectorX(i), generateDetectorY(j)) for i in range(NUM_DETECTORS)] for j in range(NUM_ROWS)}

		self.generateFrequencies()

		self.solveFreq()

	def generateFrequencies(self):
		self.frequencies = [FREQ_LOW + i*FREQ_DIFF for i in itertools.takewhile(lambda x: FREQ_LOW + x *FREQ_DIFF < FREQ_HIGH, range((FREQ_HIGH-FREQ_LOW)/FREQ_DIFF))]

	def printDetectors(self):
		detectorList = self.detectorDict[0]
		for detector in detectorList:
			print detector.returnLoc()

	def printLocations(self):
		for port in self.portList:
			print port.returnLoc()

	def calculateDist(self, port, detector):
		return ((port.returnLoc() - detector.returnLoc()[0])**2 + (detector.returnLoc()[1])**2)**0.5

	def getWavelength(self, freq):
		return SPEED_OF_SOUND/freq

	def getWavenumber(self, freq):
		return 2.0*math.pi/self.getWavelength(freq)

	#creates a dictionary of detectors to ports of the constants 
	def calculateConst(self, freq, iterNum):
		self.getDistanceDict()
		self.constDict = {}
		for detector in self.detectDistDict:
			tempDistList = self.detectDistDict[detector]
			self.constVector = []
			for dist in tempDistList:
				# print "tempDist type is: ", type(dist)
				calcConst = math.e**(complex(0,-1)*(self.getWavenumber(freq)*dist))/dist
				self.constVector.append(calcConst)
			self.constDict[detector] = self.constVector[:]

		self.calculateDifferences(iterNum)


	#calculates the differences between detectors to form a matrix
	def calculateDifferences(self, iterNum):
		midPoint = len(self.detectorDict[iterNum])/2-1
		refDetector = self.detectorDict[iterNum][midPoint]
		refList = self.constDict[refDetector]

		for detector in self.constDict:
			# if detector == refDetector:
				# continue
			tempConstList = self.constDict[detector]
			tempResu = [i-j for i, j in zip(tempConstList, refList)]
			self.diffMatrix.append(tempResu)

	#creates a dictionary from detectors to a list of distances from ports
	def getDistanceDict(self):
		self.detectDistDict = {}
		for detector in self.detectorList:
			self.distanceList = []
			for port in self.portList:
				self.distanceList.append(self.calculateDist(port, detector))
			self.detectDistDict[detector] = self.distanceList[:]

		#validation code 
		keys = self.detectDistDict.keys()
		for i in range(len(self.detectDistDict)-1):
			for j in range(i+1, len(self.detectDistDict)):
				if self.detectDistDict[keys[i]] == self.detectDistDict[keys[j]]:
					print "whoops"

	#Gets a larger dictionary of the constants lol 
	def getfullConstDict(self, freq):
		self.tempDict = {}
		for key in self.detectorDict:
			self.detectorList = self.detectorDict[key]
			self.getDistanceDict()
			self.tempDict[key] = self.detectDistDict

		self.concatenateDicts()
		self.fullConstDict = {}
		self.fullDiffDict = {}

		#constructs the constant na ddiff dict 
		for key in self.tempDict:
			tempDict = {}
			for detector in self.tempDict[key]:
				tempDistList = self.updateDistDict[detector]
				self.constVector = [math.e**(complex(0, -1)  * self.getWavenumber(freq) * dist)/dist for dist in tempDistList]
				tempDict[detector] = copy.copy(self.constVector)
			self.fullConstDict[key] = tempDict

			midpoint = len(self.detectorDict[key])/2-1
			refDetector = self.detectorDict[key][midpoint]
			refList = self.fullConstDict[key][refDetector]
			
			tempDict = {}
			for detector in self.fullConstDict[key]:
				diffList = [i-j for i, j in zip(self.fullConstDict[key][detector], refList)]
				tempDict[detector] = diffList

			self.fullDiffDict[key] = tempDict



	#Do I need this code?
	def getRefDict(self, iterNum):
		midpoint = len(self.detectorDict[iterNum])/2-1
		self.refDetector = self.detectorDict[iterNum][midPoint]

	def concatenateDicts(self):
		self.updateDistDict = {}
		for key in self.tempDict:
			self.updateDistDict.update(self.tempDict[key])


	def solveFreq(self):
		for freq in self.frequencies:
			self.solveSystem(freq)

	#eps defines the accuracy of the solution 
	#calculates solutions to the nullspace
	#eps needs to be adjusted depending upon the number of ports we're working with 
	def nullSpace(self, eps = 1.5e-10):
		u, s, vh = np.linalg.svd(self.diffMatrix)
		self.null_space = np.compress(s <=eps, vh, axis = 0)
		return self.null_space.T

	def solveSystem(self, freq):
		self.pressureDict = {}
		self.errorDict = {}
		self.diffMatrix = []
		for key in self.detectorDict:
			self.detectorList = self.detectorDict[key]
			self.calculateConst(freq, key)
			

		eps = 1.5e-15
		while True:
			self.result = self.nullSpace(eps).T
			if self.checkResu(freq):
				break
			eps *= 2 if self.result.shape[0] == 0 else 1/1.5
			# print eps


	def checkResu(self, freq):
		if self.result.shape[0] != 1:
			return False
		self.getfullConstDict(freq)
		self.calculatePressure()
		return True

	def calculatePressure(self):
		self.pressureDict = {}
		for key in self.fullConstDict:
			self.pressureDict[key] = {detector: (np.dot(self.fullConstDict[key][detector], self.result.T), detector.returnLoc()) for detector in self.fullConstDict[key]}

	def returnPressure(self):
		return self.pressureDict

	def returnError(self):
		return self.errorDict

	def getResult(self):
		return self.result



if __name__ == "__main__":
	calculation = runCalculation()
	pressures = calculation.returnPressure()
	errors = calculation.returnError()
	print pressures

	# print errors[0]
	# print len(errors[0])












