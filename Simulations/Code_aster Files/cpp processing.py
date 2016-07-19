#including import statments
import csv 
import os
gtw = __import__("get transmission weights")
import get_identity_matrix as getIndependent_Base #needed for an export class lol 



#defines the number of simulations run for confirmation
NUM_CYCLES = 2

ARR_ONE = [0, 1]#, 0, 0]
ARR_TWO = [1, complex(1,5)]#, 0, 0]
# ARR_THREE = [0, 0, 1, 0]
# ARR_FOUR = [0, 0, 0, 1]
VELOCITY_MATRIX = [ARR_ONE, ARR_TWO]#, ARR_THREE, ARR_FOUR]

#including file constants
FILEPATH = "Paper/rightFreq identity/Two Cells complex"
FILENAME = "Two Cell Simulation csv.txt"
WEIGHTS_OUTPUT = "two cell calculated weights new"

#Dictionary Keys that we want
PRES_0_real = 'pressure 0 real'
PRES_0_imag = 'pressure 0 imag'
PRES_1_real = 'pressure 1 real'
PRES_1_imag = 'pressure 1 imag'
PRES_2_real = 'pressure 2 real'
PRES_2_imag = 'pressure 2 imag'
PRES_3_real = 'pressure 3 real'
PRES_3_imag = 'pressure 3 imag'
PRES_4_real = 'pressure 4 real'
PRES_4_imag = 'pressure 4 imag'



PRES_6_real = 'pressure 6 real'
PRES_6_imag = 'pressure 6 imag'



#helper funciton used to strip the last term of a lines
def stripEnd(line):
	line = line.strip("\n")
	return line

class updateClasses(object):
	def __init__(self):
		gtw.updateClass(NUM_CYCLES, VELOCITY_MATRIX)
		getIndependent_Base.updateClass(NUM_CYCLES)


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

	#generates the parameters for the dictionary
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
		self.tm = transmissionMatrix
		self.frequencies = self.tm[0].keys()
		self.generatePresKeys()
		self.solveMatrix()

	def generatePresKeys(self):
		self.presKeys = [PRES_0_real, PRES_0_imag, PRES_6_real, PRES_6_imag]
		# self.presKeys = [PRES_0_real, PRES_0_imag, PRES_1_real, PRES_1_imag, PRES_2_real, PRES_2_imag, PRES_3_real, PRES_3_imag]


	def createcomplexPres(self, freq, presNumber):
		self.tempComplex = []
		for i in range(NUM_CYCLES):
			self.tempComplex.append(complex(float(self.tm[i][freq][self.presKeys[presNumber*2]]), float(self.tm[i][freq][self.presKeys[presNumber*2 +1]])))
			print "real is: ", self.tm[i][freq][self.presKeys[presNumber*2]], "imag is: ",  self.tm[i][freq][self.presKeys[presNumber*2 + 1]]
		# print self.tempComplex
		# self.tempComplex.append(complex(float(self.tm[0][freq][self.presKeys[presNumber]]), float(self.tm[])))


	#gets
	def getPressure(self, freq, index):
		self.pressureVector = []
		self.createcomplexPres(freq, index)
		self.pressureVector = self.tempComplex
		# for i in range(NUM_CYCLES):
			# self.pressureVector.append(self.tempComplex[i])


def main():
	updateClasses()
	PVDict = loadFile().getCSV()
	# print PVDict[0][25000.0]
	# print PVDict[1][25000.0]
	tw = calculateTransmission(PVDict)
	rtw = tw.returnWeights()
	# print rtw[0][32764.0]
	getIndependent_Base.exportIdentity(rtw, FILEPATH, WEIGHTS_OUTPUT)

main()

