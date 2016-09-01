'''
From the cpp file where we're resolving for new boundary conditions
this file allows for calculation of the transmission and transmission prime matrices


NOTE: This module might be slightly incomplete
'''

#including import statments
import csv 
import os
gtw = __import__("get transmission weights")
import get_identity_matrix as getIndependent_Base #needed for an export class lol
getIndependent = __import__("Independent Matrix")




#defines the number of simulations run for confirmation
#This number should match the number of ports to get a stable solution
#to the linear algebra system 
NUM_CYCLES = 4

ARR_ONE = [5, 0, 0, 0]
ARR_TWO = [0, 5, 0, 0]
ARR_THREE = [0, 0, 5, 0]
ARR_FOUR = [0, 0, 0, 5]
VELOCITY_MATRIX = [ARR_ONE, ARR_TWO, ARR_THREE, ARR_FOUR]

VELOCITY_VECTOR = [0] * NUM_CYCLES #Used in finding the independent matrix

#including file constants
FILEPATH = "Paper/Two Cells Four Ports"
FILENAME = "simulation names csv.txt"
WEIGHTS_OUTPUT = "Two cells 4 Ports calculated weights"
IDENTITY_OUTPUT = "calculated transmission prime output"
PORTFILE = "ports.txt"
ORIG_ARR = [] #Used in getOriginalMatrix
TRANS_ARR = [] #used in getTransmission


def updateClass(numCycles, velocityMatrix):
	global NUM_CYCLES, VELOCITY_MATRIX
	NUM_CYCLES = numCycles
	VELOCITY_MATRIX = velocityMatrix

	VELOCITY_VECTOR = [complex(0, 0)] * NUM_CYCLES
	ORIG_ARR = [2*i +1 for i in range(NUM_CYCLES/2)]
	TRANS_ARR = [2*i for i in range(NUM_CYCLES/2)]

#helper funciton used to strip the last term of a lines
def stripEnd(line):
	line = line.strip("\n")
	return line

#updates the classes we're calling functions from 
class updateClasses(object):
	def __init__(self):
		updateClass(NUM_CYCLES, VELOCITY_MATRIX) #need this temporarily to allow for stuff to run smoothly
		gtw.updateClass(NUM_CYCLES, VELOCITY_MATRIX)
		getIndependent_Base.updateClass(NUM_CYCLES)
		getIndependent.updateClass(NUM_CYCLES, VELOCITY_MATRIX)

#loads the outputted CSV file from cpp processing
#results in 
class loadFile(object):
	def __init__(self):
		self.DIR = os.path.dirname(__file__)
		self.loadFilenames()
		self.loadSimulations()

	def getCSV(self):
		return self.finalSim

	#from the filename path, load all of the filenames that will need to be read into a list
	def loadFilenames(self):
		filePath = os.path.join(self.DIR, FILEPATH, FILENAME)
		with open(filePath) as f:
			lines = f.readlines()
			for i in range(len(lines)):
				lines[i] = stripEnd(lines[i])
		self.args = lines

	def loadSimulations(self):
		self.finalSim = []
		for self.tempFile in self.args:
			self.loadCSV()
			self.finalSim.append(self.mapping)

	#generates the parameters for the dictionary for extracting
	#gets rid of blanks and frequency parameters
	def generateParams(self, row):
		self.params = []
		for key in row.keys():
			if key == '' or key == 'Frequency':
				continue
			self.params.append(key)

	#each row is a dictionary and adds it to the temporary dictionary
	#each round a new tempDict is reinitialized
	#so the resultant dictionary is from frequency to weights
	def getRow(self, row):
		self.tempDict = {}
		for key in self.params:
			self.tempDict[key] = row[key]

	#load a single CSV file into a dictionary
	def loadCSV(self):
		self.mapping = {}
		print self.tempFile
		tempPath = os.path.join(self.DIR, FILEPATH, self.tempFile + ".csv")
		csvfile = open(tempPath, "r")
		reader = csv.DictReader(csvfile)

		for row in reader:
			self.generateParams(row)
			self.getRow(row)
			self.mapping[float(row["Frequency"])] = self.tempDict

class calculateTransmission(gtw.getTransmissionWeights):
	def __init__(self, transmissionMatrix):
		self.dir = os.path.dirname(__file__)
		self.tm = transmissionMatrix
		self.frequencies = self.tm[0].keys()
		self.generatePresKeys(PORTFILE)
		self.solveMatrix()

	#generates the pressure keys based upon the import file 
	def generatePresKeys(self, portFile):
		filePath = os.path.join(self.dir, FILEPATH, PORTFILE)
		presNumbers = []
		with open(filePath) as f:
			lines = f.readlines()
			for i in range(len(lines)):
				lines[i] = stripEnd(lines[i])
				presNumbers += lines[i].split(',')

		presNumbers = [str(int(presNumbers[i])-1) for i in range(NUM_CYCLES)] #needed for normalization because I was lazy in CPP

		#generates a tuple for pressure keys
		self.presKeys = [("pressure " + presNumbers[i] + " real", "pressure " + presNumbers[i] + " imag") for i in range(NUM_CYCLES)]
		print "the keys are: ", self.presKeys
		print len(self.presKeys), " is num of keys"

	#presNumber represents which pressure number is being solved for 
	def createcomplexPres(self, freq, presNumber):
		#list generation to get the values from pressures
		self.tempComplex = [complex(float(self.tm[i][freq][self.presKeys[presNumber][0]]), float(self.tm[i][freq][self.presKeys[presNumber][1]])) for i in range(NUM_CYCLES)]


	#overrides getTransmissionWeight's method of get pressure
	#results in a manipulation of the current passed in function 
	#index represents which pressure you're solving for 
	def getPressure(self, freq, index):
		self.createcomplexPres(freq, index)
		self.pressureVector = self.tempComplex

	#helper function to return presKeys
	def returnPresKeys(self):
		return self.presKeys

#class to go and get the transmission prime from the cpp values 
#tm in this case is the tm generated from the cpp code
#I don't think I ever finished this??? 
class transmissionPrime(getIndependent.independentMatrix):
	def __init__(self, transmissionMatrix, velocityVector, frequencies, presKeys):
		self.tm = transmissionMatrix
		self.presKeys = presKeys
		self.velocityMatrix = velocityVector
		self.freq = frequencies
		# self.getTransmission()

	def generateComplex(self, freq, index):
		tempTuple = self.presKeys[index]
		self.tempPress = complex(self.tm[index][freq][tempTuple[0]], self.tm[index][freq][tempTuple[1]])

	def getOrigMatrix(self, freq):
		arrStor = []
		for i in range(NUM_CYCLES):
			tempArr = [0] * NUM_CYCLES



#quick code to run everything instead of throwing it into main because I feel like it
class runProcessing:
	def __init__(self):
		updateClasses()
		self.PVDict = loadFile().getCSV()
		self.tw = calculateTransmission(self.PVDict)
		self.rtw = self.tw.returnWeights()
		self.presKeys = self.tw.returnPresKeys()
		frequencies = self.rtw.keys()
		# transmissionPrime(self.PVDict)
		transmissionPrime(self.rtw, VELOCITY_VECTOR, frequencies, self.presKeys)
		#getIndependent_Base.exportIdentity(rtw, FILEPATH, WEIGHTS_OUTPUT) #right now commented out because I don't want it to export anything 
		# print frequencies
if __name__ == "__main__":
	runProcessing()


