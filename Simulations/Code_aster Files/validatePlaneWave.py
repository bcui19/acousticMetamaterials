import sys

#Define constants
NUM_PORTS = 2;
pressureVector = [complex(5,1), complex(4,1)] #for now two ports
velocityVector = [complex(5,1), complex(4,1)] #for now two ports


#takes in pressure and velocity vectors and determines if the two are components
#of valid plane waves 
#takes in the number of ports which indicates 
class planeWave_Validation(object):
	def __init__(self, pressureVector, velocityVector, numPorts):
		self.numPorts = numPorts
		self.pressure = pressureVector
		self.velocity = velocityVector

	def globalValidation(self):
		for i in range(self.numPorts):
			currPressure = self.pressure[i]
			currVelocity = self.velocity[i]
			if not self.validate(currPressure, currVelocity):
				print "we fucked up at iteration: ", i
				print "values are (pressure, velocity) : (", currPressure, " ", currVelocity, ")"
				break
		print "the phase of the two waves are the same"

	def validate(self, currPressure, currVelocity):
		realRatio = self.checkReal(currPressure, currVelocity)
		imagRatio = self.checkImag(currPressure, currVelocity)
		return True if realRatio == imagRatio else False

	def checkReal(self, currPressure, currVelocity):
		return currPressure.real/currVelocity.real

	def checkImag(self, currPressure, currVelocity):
		return currPressure.imag/currVelocity.imag

if __name__ == "__main__":
	planeWave = planeWave_Validation(pressureVector, velocityVector, NUM_PORTS)
	planeWave.globalValidation()


