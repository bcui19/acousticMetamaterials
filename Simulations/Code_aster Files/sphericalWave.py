import math
NUMPORTS = 7
PERIODICITY = 3.275
AMPLITUDE = [5, 1*10**(-3)] #expressed as [v, p]
FREQUENCY = 25000
DELTA = 1
SPEED_OF_SOUND = 343.21 #in m/s
RHO = 1.2041 #density of air 


#given n input ports, calculates the spherical velocity for the given ports
class sphericalWave(object):
	'''
	Takes in a few arguments
	numPorts: the number of input ports into the system
	periodicity: the periodic spacing of the cells (center to center should be the same as before but regardless) in mm
	Amplitude: the amplitude of velocity and pressure (done as a list)
	frequency: represents teh current frequency to calculate for
	rho: density of air at a certain temperature
	speed: speed of sound propagation
	'''
	def __init__(self, numPorts, periodicity, amplitude, frequency, rho, speed):
		self.numPorts = numPorts
		self.periodicity = periodicity/1000
		self.amplitude = amplitude
		self.frequency = frequency
		self.rho = rho
		self.speed = speed
		
		self.wavelength = speed/self.frequency

	#yDistance is in millimeters
	def createVectors(self, yDistance):
		yDist = yDistance/1000
		midpoint = (self.numPorts-1)/2 #assume that the midpoint of the collimator is directly in front of the source
		self.location = [(abs(i-midpoint) * self.periodicity, yDist) for i in range(self.numPorts)]

	#given an input tuple, calculate the distance
	def calculateDistance(self, currTuple):
		currX = currTuple[0]
		currY = currTuple[1]
		return (currX**2 + currY**2)**0.5

	#calculates the amount of time elapsed given the wave traveling at the speed of sound 
	def calculateTime(self, currTuple):
		# distance = self.calculateDistance(currTuple)
		distance = lambda currTuple: (currTuple[0]**2 + currTuple[1]**2)**0.5
		print "fucking distance right now is: ", distance(currTuple)
		self.distances.append(distance(currTuple))
		print "distance vector now is: ", self.distances
		print type(distance(currTuple)/self.speed)
		return distance(currTuple)/self.speed

	#some weird euler's formula stuff to get the velocity 
	def getComplex_Velocity(self, iteration):
		currTime = self.time[iteration]
		currDist = self.distances[iteration]
		realComponent = math.cos(2*math.pi*currDist/self.wavelength-2*math.pi*currTime*self.frequency)
		imagComponent = math.sin(2*math.pi*currDist/self.wavelength-2*math.pi*currTime*self.frequency)
		return realComponent - complex(0,1) *imagComponent

	#need to take in velocity amplitude
	def velocityAlg(self, iteration):
		return 1.0*self.amplitude[1]/(self.rho * self.speed * self.distances[iteration]) * (1.0 - complex(0.0,1.0)/(2*math.pi*self.wavelength * self.distances[iteration]))*self.getComplex_Velocity(iteration)

	def calculateVelocity(self, yDistance):
		self.velocityVector = [self.pressureVector[it]/self.rho/self.speed*(1-complex(0,1)/(2*math.pi*self.distances[it]*self.wavelength)) for it in range(self.numPorts) ]
		print self.velocityVector
		# self.distances = []
		# self.createVectors(yDistance)
		# self.time = [self.calculateTime(cell) for cell in self.location]
		# self.velocityVector = [self.velocityAlg(it) for it in range(self.numPorts)]
		# print self.velocityVector

	def getComplex_pressure(self, iteration):
		print "iteration is: ", iteration
		currTime = self.time[iteration]
		print "currTime is: ", currTime
		currDist = self.distances[iteration]
		print "currDist is: ", currDist
		print "wavelength is: ", self.wavelength
		realComp = math.cos(2.0*math.pi*currDist/self.wavelength - 2.0*math.pi*currTime*self.frequency)
		imagComp = math.sin(2.0*math.pi*currDist/self.wavelength - 2.0*math.pi*currTime*self.frequency)
		print "realComp is: ", realComp, " imag comp is: ", imagComp
		return realComp - complex(0.0,1.0) * imagComp

	def pressureAlg(self, iteration):
		return self.amplitude[1] * self.getComplex_pressure(iteration)/self.distances[iteration]

	#assumes calculated after velocity
	def calculatePressure(self, yDistance):
		self.distances = []
		self.createVectors(yDistance)
		self.time = [self.calculateTime(cell) for cell in self.location]
		self.pressureVector = [self.pressureAlg(it) for it in range(self.numPorts)]
		print "pressureVector is: ", self.pressureVector

	#returns the pressure and velocity vectors to be used
	def calculateWaves(self, yDistance):
		self.calculatePressure(yDistance)
		self.calculateVelocity(yDistance)
		print "finalVals are: ", self.velocityVector, self.pressureVector
		return self.velocityVector, self.pressureVector

if __name__ == "__main__":
	wave = sphericalWave(NUMPORTS, PERIODICITY, AMPLITUDE, FREQUENCY, RHO, SPEED_OF_SOUND)
	velocityVector, pressureVector = wave.calculateWaves(10.0) #distance of 10mm from the source






