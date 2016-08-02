import math
import itertools
#some mathematical constants that seem somewhat useful
ARBITRARY_AMPLITUDE = complex(5.3, 1.4)
SPEED_OF_SOUND = 343.21 #in m/s
RHO = 1.2041 #density of air 


#define constants
NUM_PORTS = 10
NUM_DETECTORS = 50
DETECTOR_MID = NUM_DETECTORS/2.0
NUM_ROWS = 1

PORT_SPACING = 0.005
DETECTOR_SPACING = 0.0025
ROW_SPACING = 0.5

MIDPOINT = (NUM_PORTS-1)/2.0 * PORT_SPACING

FREQ_LOW = 25000
FREQ_HIGH = 30000
FREQ_DIFF = 12

def generateSourceLoc(port_NUM):
	return port_NUM * PORT_SPACING

def generateDetectorX(detectorNum):
	return MIDPOINT + (detectorNum - DETECTOR_MID+1) * DETECTOR_SPACING

def generateDetectorY(rowNum):
	return (rowNum + 1) * ROW_SPACING

class source(object):
	def __init__(self, xloc, amplitude, velocity):
		self.velocity = velocity
		self.location = (xloc, 0)
		self.amplitude = amplitude
		self.pressure = {}

	def returnLoc(self):
		return self.location

	def calcDistance(self, detector):
		return ((self.location[0] - detector.returnLoc()[0])**2 + (self.location[1] - detector.returnLoc()[1])**2)**0.5

	def calculateWavelength(self, frequency):
		return self.velocity/frequency

	def calculateWavenumber(self, frequency):
		return 2*math.pi/self.calculateWavelength(frequency)

	#passing in a detector object
	def calculatePressure(self, detector, frequency):
		tempDist = self.calcDistance(detector)
		complexComponent = math.e ** (complex(0, -1)*(self.calculateWavenumber(frequency)*tempDist))
		try:
			currList = self.pressure[frequency]
			currList.append((detector, self.amplitude/tempDist *complexComponent))
			self.pressure[frequency] = currList
		except KeyError:
			tempList = [(detector, self.amplitude/tempDist * complexComponent)]
			self.pressure[frequency] = tempList

		return self.amplitude/tempDist * complexComponent


#detector is treated as a tuple 
class detector:
	def __init__(self, xloc, yloc):
		self.location = (xloc, yloc)
		self.pressure = {}

	def returnLoc(self):
		return self.location

	def sumPressure(self, freq, port):
		currPressure = self.pressure[freq] if freq in self.pressure else 0
		temptupleList = port[freq]
		finIndex = 0
		for i in range(len(temptupleList)):
			currDetector = temptupleList[i]
			currLocation = currDetector.returnLoc()
			if currLocation == self.location:
				print "it works"
				finTuple = finIndex




class runGeneration:
	def __init__(self):
		self.portList = [source(generateSourceLoc(i), ARBITRARY_AMPLITUDE, SPEED_OF_SOUND) for i in range(NUM_PORTS)]
		self.detectorList = [detector(generateDetectorX(i), generateDetectorY(j)) for i in range(NUM_DETECTORS) for j in range(NUM_ROWS)]
		self.generateFrequencies()
		# print self.frequencies
		self.generatePressure()

	def generateFrequencies(self):
		self.frequencies = [FREQ_LOW + i*FREQ_DIFF for i in itertools.takewhile(lambda x: FREQ_LOW + x *FREQ_DIFF < FREQ_HIGH, range((FREQ_HIGH-FREQ_LOW)/FREQ_DIFF))]

	#generates pressures for a broad range of frequencies
	def generatePressure(self):
		self.generatePortPressure()
		self.generateDetecturePressure()

	def generateDetectorPresure(self):
		for detector in self.detectorList:
			detector.sumPressure(freq, port (for freq in self.frequencies) (for port in self.portList))

	def generatePortPressure(self):
		for i in range(NUM_PORTS):
			for j in range(NUM_DETECTORS * NUM_ROWS):
					currDetector = self.detectorList[j]
					for freq in self.frequencies:
						self.portList[i].calculatePressure(currDetector, freq)

	def returnPorts(self):
		return self.portList

	def returnFreq(self):
		return self.frequencies

	def printLocations(self):
		for i in range(NUM_PORTS):
			print self.portList[i].returnLoc()
		for i in range(NUM_DETECTORS):
			print self.detectorList[i].returnLoc()
		# print len(self.detectorList)

class validate:
	def __init__(self, generator):
		self.generator = generator
		self.portList = self.generator.returnPorts()
		self.frequencies = self.generator.returnFreq()

		self.validateFreq()

	def validateFreq(self):
		for freq in self.frequencies:
			for port in portList:
				self.validatePort(port, freq)

	# def validatePort(self, port, freq):


if __name__ == "__main__":
	generator = runGeneration()
	validate(generator)
	print math.e**(complex(0,1)*math.pi)





