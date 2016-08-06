import numpy as np 
import matplotlib.pyplot as plt


calcWave = __import__("Plane Wave Least Squares")


class imPlotting:
	def __init__(self, pressures):
		self.pressures = pressures
		self.plot()

	def plot(self):
		self.generateArr()
		im = plt.imshow(self.arr, cmap = "rainbow")
		plt.autoscale(enable = True, axis = 'both', tight = None)
		plt.colorbar(im, orientation = "horizontal")
		plt.show()

	def generateArr(self):
		self.arr = []
		for key in self.pressures:

			self.arr.append([self.pressures[key][detector][0].real for detector in self.pressures[key]])
		# print self.arr


# if __name__ == "__main__":
# 	planeWave = calcWave.runCalculation()
# 	pressures = planeWave.returnPressure()
# 	imPlotting(pressures)

