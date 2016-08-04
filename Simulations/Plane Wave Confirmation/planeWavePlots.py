calcPlane = __import__("Plane Wave LinAlg")
import numpy as np
import math
import itertools
import matplotlib.pyplot as plt

#define constants
NUM_PORTS = 11
NUM_DETECTORS = 20
DETECTOR_MID = NUM_DETECTORS/2.0
NUM_ROWS = 10


class graphResu():
	def __init__(self, pressureVals):
		self.pressureVals = pressureVals
		self.graphPressure()

	def graphPressure(self):
		numPoints = NUM_DETECTORS * NUM_ROWS
		self.xLoc = self.generateLoc(0)
		self.yLoc = self.generateLoc(1)
		self.generateColors()

		area = np.pi * (15)**2

		plt.scatter(self.xLoc, self.yLoc, s= area, c=self.colors, alpha = 0.5)
		plt.show()


	def generateLoc(self, inputVal):
		locList = []
		for detector in self.pressureVals:
			locList.append(self.pressureVals[detector][1][0 if inputVal == 0 else 1])
		# for key in self.pressureVals:
		# 	detectorList = self.pressureVals[key].keys()
		# 	for detector in detectorList:

		# 		locList.append(self.pressureVals[key][detector][1][0 if inputVal == 0 else 1])
		return locList

	def generateColors(self):
		self.colors = []
		for key in self.pressureVals:
			self.getColor(key)
			self.colors += self.tempColor

	def getColor(self, key):
		# detectorList = self.pressureVals[key].keys()
		scalingFactor = 1e4
		previousFactor = scalingFactor
		while True:
			for detector in self.pressureVals:
				pressure = abs(self.pressureVals[detector][0]).real
				if pressure * scalingFactor < 0.5:
					previousFactor = scalingFactor
					scalingFactor *= 2
					break
				elif pressure * scalingFactor > 1.0:
					previousFactor = scalingFactor
					scalingFactor /= 1.5
					break

			if previousFactor == scalingFactor:
				tempBool = False
				break
			else:
				# print "difference is: ", previousFactor - scalingFactor
				# print "previous Factor is: ", previousFactor, "scaling Factor is: ", scalingFactor
				previousFactor = scalingFactor
		
		self.tempColor = [(0, 1, abs(self.pressureVals[detector][0].real)*scalingFactor) for detector in self.pressureVals]


class graphDiff(graphResu):
	def __init__(self, pressureVals, error):
		self.pressureVals = pressureVals
		self.error = error
		self.graphPressure()
		# self.getColor(0)

	def getColor(self, key):
		detectorList = self.pressureVals[key].keys()
		print "keys are: ", self.error.keys()
		self.errorRatio = [abs(self.error[key][i]/self.pressureVals[key][detectorList[i]][0]) for i in range(len(detectorList)-1)]

		scalingFactor = 10
		previousFactor = scalingFactor
		while True:
			for ratio in self.errorRatio:
				calcRatio = abs(math.log(ratio, 10))
				if calcRatio * scalingFactor < 0.1:
					previousFactor = scalingFactor
					scalingFactor *= 2
					break
				elif calcRatio * scalingFactor > 1.0:
					prevousFactor = scalingFactor
					scalingFactor /= 2.5
					break
			if previousFactor == scalingFactor:
				break
			else:
				# print "previous Factor is: ", previousFactor, "scaling Factor is: ", scalingFactor
				previousFactor = scalingFactor



		print "self.errorRatio is:", self.errorRatio
		self.tempColor = [(0, 0, abs(math.log(self.errorRatio[i],10))*scalingFactor) for i in range(len(detectorList)-1)]




if __name__ == "__main__":
	planeWave = calcPlane.runCalculation()
	pressures = planeWave.returnPressure()
	error = planeWave.returnError()
	graphResu(pressures)
	# graphDiff(pressures, error)










