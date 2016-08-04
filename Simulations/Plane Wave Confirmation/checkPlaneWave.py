'''
code to see differences of the plane wave
'''
waveCalculation = __import__("Plane Wave LinAlg")


class pressureDiff:
	def __init__(self, pressures):
		self.pressures = pressures
		self.difference()



	def difference(self):
		for key in self.pressures:
			for i in range(len(self.pressures)):
				tempKeys = self.pressures.keys()
				print "real diff is:", self.pressures[key][1][0] - self.pressures[tempKeys[i]][1][0]
				print "imag diff is: ", self.pressures[key][1][1] - self.pressures[tempKeys[i]][1][1]





if __name__ == "__main__":
	planeWave = waveCalculation.runCalculation()
	pressures = planeWave.returnPressure()
	aVals = planeWave.getResult()
	print aVals
	pressureDiff(pressures)