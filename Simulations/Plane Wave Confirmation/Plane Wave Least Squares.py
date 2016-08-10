import numpy as np
import plotImShow as plot
import matplotlib.pyplot as plt
waveCalculation = __import__("Plane Wave LinAlg")


#define constants
NUM_PORTS = 11
NUM_DETECTORS = 100
DETECTOR_MID = NUM_DETECTORS/2
NUM_ROWS = 50

PORT_SPACING = 0.0011375
DETECTOR_SPACING = 0.00005
ROW_SPACING = 0.0005
DETECTOR_OFFSET = 0.1

class leastSquaresWave(waveCalculation.runCalculation):
	def solveSystem(self, freq):
		self.pressureDict = {}
		self.errorDict = {}
		self.diffMatrix = []
		for key in self.detectorDict:
			self.detectorList = self.detectorDict[key]
			self.calculateConst(freq, key)

		self.constructRHS()
		self.result =  np.linalg.lstsq(self.diffMatrix, self.rhs, rcond = 1e-20)[0]
		# print self.result 


		self.getfullConstDict(freq)
		self.calculatePressure()
		# print self.pressureDict
		self.differences = {key : {detector: np.dot(self.fullDiffDict[key][detector], self.result) for detector in self.fullDiffDict[key]} for key in self.fullDiffDict }
		# print self.differences.keys()
		# key = self.differences[0].keys()[0]
		self.getMaxDiff()
		self.graphXDecay()

	def getMaxDiff(self):
		self.maxDiff = complex(0,0)
		for key in self.differences:
			# if key == 0:
				# continue
			for detector in self.differences[key]:
				self.maxDiff = self.differences[key][detector] if np.absolute(self.differences[key][detector]) > np.absolute(self.maxDiff) else self.maxDiff

		print "Max diff is: ", self.maxDiff
		print "result vector is: \n", self.result
		print "midpoint is: ", self.result[(NUM_PORTS)/2]

	def constructRHS(self):
		self.rhs = [-self.diffMatrix[i][(NUM_PORTS)/2] for i in range(len(self.diffMatrix))]
		print "rhs is: ", self.rhs

# def calculatePressure(self):
# 		self.pressureDict = {}
# 		for key in self.fullConstDict:
# 			self.pressureDict[key] = {detector: (np.dot(self.fullConstDict[key][detector], self.result.T), detector.returnLoc()) for detector in self.fullConstDict[key]}


	def graphXDecay(self):
		x = [(i+1) * DETECTOR_SPACING for i in range(NUM_DETECTORS)]
		y = [self.pressureDict[20][detector][0].real for detector in self.pressureDict[20]]

		print y
		plt.plot(x, y, "k")
		plt.show()




if __name__ == "__main__":
	waveCalculation.globalUpdate(NUM_ROWS, NUM_PORTS, NUM_DETECTORS)
	waveCalculation.spacingUpdate(dspacing = DETECTOR_SPACING, dOffset = DETECTOR_OFFSET)
	planarWave = leastSquaresWave()
	pressures = planarWave.returnPressure()
	planarWave.graphXDecay()
	# plot.imPlotting(pressures)


