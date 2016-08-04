import numpy as np
import plotImShow as plot
waveCalculation = __import__("Plane Wave LinAlg")


#define constants
NUM_PORTS = 11
NUM_DETECTORS = 20
DETECTOR_MID = NUM_DETECTORS/2
NUM_ROWS = 10



class leastSquaresWave(waveCalculation.runCalculation):
	def solveSystem(self, freq):
		self.pressureDict = {}
		self.errorDict = {}
		self.diffMatrix = []
		for key in self.detectorDict:
			self.detectorList = self.detectorDict[key]
			self.calculateConst(freq, key)

		self.constructRHS()
		self.result =  np.linalg.lstsq(self.diffMatrix, self.rhs, rcond = 1e-3)[0]
		# print self.result 


		self.getfullConstDict(freq)
		self.calculatePressure()
		# print self.pressureDict
		self.differences = {key : {detector: np.dot(self.fullDiffDict[key][detector], self.result) for detector in self.fullDiffDict[key]} for key in self.fullDiffDict }
		# print self.differences.keys()
		print len(self.differences[0])

	def constructRHS(self):
		self.rhs = [self.diffMatrix[i][(NUM_PORTS-1)/2] for i in range(len(self.diffMatrix))]
		# print self.rhs



if __name__ == "__main__":
	waveCalculation.globalUpdate(NUM_ROWS, NUM_PORTS, NUM_DETECTORS)
	planarWave = leastSquaresWave()
	pressures = planarWave.returnPressure()
	plot.imPlotting(pressures)


