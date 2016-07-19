#including import statments
import csv 
import os
gtw = __import__("get transmission weights")
import get_identity_matrix as getIndependent_Base #needed for an export class lol 



#defines the number of simulations run for confirmation
#This number should match the number of ports to get a stable solution
#to the linear algebra system 
NUM_CYCLES = 2

ARR_ONE = [5, 0]#, 0, 0]
ARR_TWO = [0, 5]#, 0, 0]
# ARR_THREE = [0, 0, 1, 0]
# ARR_FOUR = [0, 0, 0, 1]
VELOCITY_MATRIX = [ARR_ONE, ARR_TWO]#, ARR_THREE, ARR_FOUR]

#including file constants
FILEPATH = "Paper/Two Cells identity checks"
FILENAME = "simulation names csv.txt"
WEIGHTS_OUTPUT = "v5,5/Two cells 2 Ports calculated weights"
PORTFILE = "ports.txt"


#helper funciton used to strip the last term of a lines
def stripEnd(line):
	line = line.strip("\n")
	return line

#updates the classes we're calling functions from 
class updateClasses(object):
	def __init__(self):
		gtw.updateClass(NUM_CYCLES, VELOCITY_MATRIX)
		getIndependent_Base.updateClass(NUM_CYCLES)

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

	#each row is a dictionary
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

		presNumbers = [str(int(presNumbers[i])-1) for i in range(NUM_CYCLES)] #needed for normalizatoin because I was lazy in CPP

		#generates a tuple for pressure keys
		self.presKeys = [("pressure " + presNumbers[i] + " real", "pressure " + presNumbers[i] + " imag") for i in range(NUM_CYCLES)]
		print self.presKeys


	#presNumber represents which pressure number is being solved for 
	def createcomplexPres(self, freq, presNumber):
		self.tempComplex = []
		#list generation to get the values from pressures
		self.tempComplex = [complex(float(self.tm[i][freq][self.presKeys[presNumber][0]]), float(self.tm[i][freq][self.presKeys[presNumber][1]])) for i in range(NUM_CYCLES)]

		print self.tempComplex


	#overrides getTransmissionWeight's method of get pressure
	#results in a manipulation of the current passed in function 
	#index represents which pressure you're solving for 
	def getPressure(self, freq, index):
		self.pressureVector = []
		self.createcomplexPres(freq, index)
		self.pressureVector = self.tempComplex


def main():
	updateClasses()
	PVDict = loadFile().getCSV() #gets the pressure velocity dictionary to manipulate
	# print PVDict[0][25000.0]
	# print PVDict[1][25000.0]
	tw = calculateTransmission(PVDict)
	rtw = tw.returnWeights()
	# print rtw[0][32764.0]
	getIndependent_Base.exportIdentity(rtw, FILEPATH, WEIGHTS_OUTPUT)

main()

