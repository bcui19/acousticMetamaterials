import numpy as np
import plotImShow as plot
import matplotlib.pyplot as plt
waveCalculation = __import__("Plane Wave LinAlg")
leastSqPlane = __import__("Plane Wave Least Squares")

#define constants
NUM_PORTS = 11
NUM_DETECTORS = 35
DETECTOR_MID = NUM_DETECTORS/2
NUM_ROWS = 35

PORT_SPACING = 0.0011375
DETECTOR_SPACING = 0.0005
ROW_SPACING = 0.005
DETECTOR_OFFSET = 0.1

MIDPOINT = (NUM_PORTS-1)/2.0 * PORT_SPACING

def generateDetectorX(detectorNum):
	return MIDPOINT + (detectorNum - DETECTOR_MID+1) * DETECTOR_SPACING

class reducedLeastSquaresWave(leastSqPlane.leastSquaresWave):
	def solveSystem(self, freq):
		self.pressureDict = {}
		self.errorDict = {}
		self.diffMatrix = []
		for key in self.detectorDict:
			self.detectorList = self.detectorDict[key]
			self.calculateConst(freq, key)

		self.constructRHS()
		self.reduceMatrix()

		self.leastSqResu =  np.linalg.lstsq(self.reducedMatrix, self.rhs, rcond = 1e-4)[0]
		self.getSVD(freq)
		# print self.diffMatrix
		print "result is: \n", self.leastSqResu
		print "SVD result is [0]: \n", self.resultSVDResu[0]
		# print "SVD result is [1]: \n", self.resultSVDResu[1]

		tempDetector = self.fullConstDict[0].keys()[0]
		# print "detector vals are: ", self.fullConstDict[0][tempDetector]

		# self.getfullConstDict(freq)
		self.normalizeVals()
		self.calcPressure()

		# print np.dot(self.diffMatrix,self.leastSqResu)
		# print np.dot(self.diffMatrix, self.svdResu)

		# print "storage array is: ", self.storArr
		# print self.nullPressure[0]
		# print self.svdPressure[0]
		self.graphDecay(self.nullPressure, "Least Squares Pressure Plot")
		self.graphDecay(self.svdPressure, "SVD Reduced Pressure Plot")

	# def checkSolution(self):


	def normalizeVals(self):
		self.svdResu = self.resultSVDResu[0]
		self.svdResu =  np.insert(self.svdResu, NUM_PORTS/2, 1)
		self.leastSqResu = np.insert(self.leastSqResu, NUM_PORTS/2,1)


	def calcPressure(self):
		self.nullPressure = {}
		self.svdPressure = {}
		for key in self.fullConstDict:
			self.nullPressure[key] = {detector: (np.dot(self.fullConstDict[key][detector], self.leastSqResu.T), detector.returnLoc()) for detector in self.fullConstDict[key]}
			self.svdPressure[key] = {detector : (np.dot(self.fullConstDict[key][detector], self.svdResu.T), detector.returnLoc()) for detector in self.fullConstDict[key]}

	def reduceMatrix(self):
		midpoint = NUM_PORTS/2
		self.reducedMatrix = []
		self.storArr = []
		for i in range(len(self.diffMatrix)):
			tempArray = self.diffMatrix[i][:]
			# print "length of array was: ", len(tempArray)
			self.storArr.append(tempArray[midpoint-1])
			del tempArray[midpoint]
			# print "length of array now is: ", len(tempArray)
			self.reducedMatrix.append(tempArray[:])
		print "size of matrix is: ", len(self.reducedMatrix)

	def nullSpace(self, eps = 1.5e-10):
		u, s, vh = np.linalg.svd(self.reducedMatrix)
		self.null_space = np.compress(s <=eps, vh, axis = 0)
		return self.null_space.T

	def getSVD(self, freq):
		eps = 1.5e-15
		while True:
			self.resultSVDResu = self.nullSpace(eps).T
			if self.validateResu(freq):
				break
			eps *= 2 if self.resultSVDResu.shape[0] <= 1 else 1/1.5
			print "epsilon is: ", eps
		print self.resultSVDResu.shape

	def validateResu(self, freq):
		if self.resultSVDResu.shape[0] != 2:
			print self.resultSVDResu.shape[0]
			return False
		self.getfullConstDict(freq)
		return True

	def graphDecay(self, yVals, title):
		x = [(i+1) * ROW_SPACING for i in range(NUM_ROWS)]
		y = []
		for key in self.detectorDict:
			for detector in yVals[key]:
				if detector.returnLoc()[0] != generateDetectorX(DETECTOR_MID):
					continue
				y.append(yVals[key][detector][0].real)


		# print "x is : \n", x
		# print "y is : \n", y
		plt.plot(x, y, 'k')
		plt.xlabel('Distance from source')
		plt.ylabel('Pressure')
		plt.title(title)
		plt.show()



if __name__ == "__main__":
	waveCalculation.globalUpdate(NUM_ROWS, NUM_PORTS, NUM_DETECTORS)
	waveCalculation.spacingUpdate(dspacing = DETECTOR_SPACING, dOffset = DETECTOR_OFFSET, rspacing = ROW_SPACING)
	planarWave = reducedLeastSquaresWave()
	# pressures = planarWave.returnPressure()
	# plot.imPlotting(pressures)