import os 
import copy
import numpy as np
import cmath
import csv
import coalesce_files as coalesce
import get_transmission_matrix as gtm


#Define constants
NUM_CYCLES = 4
VELOCITY_SOLUTION_MATRIX = [0, 0, 0, 0]
print "type of velocity is: ", type(VELOCITY_SOLUTION_MATRIX)


class identityTransformation(object):
	def __init__(self, transmissionMatrix, frequencies):
		self.tm = transmissionMatrix
		self.freq = frequencies
		self.getTransmission()
		# self.getPressureMatrix(0, 512.0)

	def getOrigMatrix(self, freq):
		arrStor = []
		for i in range(NUM_CYCLES):
			tempArr = [0]*4
			press2 = self.tm[NUM_CYCLES + i][freq]
			tempArr[0] = press2[press2.keys()[0]] #there will only be one key
			press4 = self.tm[NUM_CYCLES*3 + i][freq]
			tempArr[2] = press4[press4.keys()[0]]
			
			tempArr[1] = complex(1, 0) if i == 1 else complex(0, 0)
			tempArr[3] = complex(1, 0) if i == 3 else complex(0, 0) 

			arrStor.append(tempArr)

		newArr = np.eye(NUM_CYCLES, dtype = complex)

		for i in range(NUM_CYCLES):
			for j in range(NUM_CYCLES):
				newArr[i][j] = arrStor[i][j]

		return newArr

	def getSolMatrix(self, index, freq):
		solArr = []
		for i in range(NUM_CYCLES):
			tempDict = self.tm[NUM_CYCLES * index + i][freq]
			solArr.append(tempDict[tempDict.keys()[0]])
		return solArr

	def getPressureMatrix(self, index, freq):
		origMatrix = self.getOrigMatrix(freq)
		solutionMatrix = self.getSolMatrix(index, freq)
		return np.linalg.solve(origMatrix, solutionMatrix)

	def getVelocityMatrix(self, index, freq):
		origMatrix = self.getOrigMatrix(freq)
		solutionMatrix = VELOCITY_SOLUTION_MATRIX[:]
		solutionMatrix[index+1] = 1
		return np.linalg.solve(origMatrix, solutionMatrix)

	def getTransmission(self):
		self.identityDict = {}
		for currFreq in self.freq:
			solArr = []
			for j in [0,2]:
				presSol = self.getPressureMatrix(j, currFreq)
				velSol = self.getVelocityMatrix(j, currFreq)
				solArr.append(presSol)
				solArr.append(velSol)

			self.identityDict[currFreq] = solArr
	
	def returnTransmission(self):
		return self.identityDict




class exportIdentity(object):
	def __init__(self, identityTransmission, folderPath, filename):
		self.identity = identityTransmission
		self.frequencies = self.identity.keys()
		self.folderPath = folderPath
		self.dir = os.path.dirname(__file__)

		# print "transmission is: ", type(self.identity[self.frequencies[0]][0][0].real)
		# print "transmisison is: ", self.identity[self.frequencies[0]][0][0].real
		# print "len is: ", len(self.identity[self.identity.keys()[0]])
		self.exportData(filename)

	#generates two fieldnames to make my life easier 
	def generatefieldnames(self):
		self.fieldnames = ["Frequency"]
		self.matrix_fieldnames = []
		for i in range(NUM_CYCLES):
			tempArr = []
			for j in range(NUM_CYCLES):
				tempArr.append("S" + str(i) + str(j) + " real")
				tempArr.append("S" + str(i) + str(j) + " imag")
			self.matrix_fieldnames.append(tempArr)
			self.fieldnames += tempArr
		# print "len of fieldnames is: ", len(self.fieldnames)

	def generateDict(self, freq):
		self.outputDict = {"Frequency": freq}
		for i in range(NUM_CYCLES):
			for j in range(NUM_CYCLES):
				self.outputDict[self.matrix_fieldnames[i][2*j]] = self.identity[freq][i][j].real
				self.outputDict[self.matrix_fieldnames[i][2*j+1]] = self.identity[freq][i][j].imag

	def exportData(self, filename):
		self.generatefieldnames()
		outputPath = os.path.join(self.dir, self.folderPath, filename + ".csv")
		csvfile = open(outputPath, "w")
		writer = csv.DictWriter(csvfile, fieldnames = self.fieldnames)
		writer.writeheader()
		# for i in range(1):
			# self.generateDict(self.frequencies[0])
			# for key in self.outputDict.keys():
			# 	print "key is: ", key
			# 	print self.outputDict[key]
		for freq in self.frequencies:
			self.generateDict(freq)
			writer.writerow(self.outputDict)


def main():
	fileDirectory = "Paper/rightFreq"
	tempOutput = "temp"
	tm = gtm.transmissionMatrix(fileDirectory + "/paperCheck.txt", fileDirectory, "collimator listennode.txt", tempOutput, 1)
	rtm = tm.returnTransmissionMatrix()
	frequencies = rtm[0].keys()
	# print rtm
	coalesce.runCoalesce(tempOutput, "coalesced", fileDirectory)
	# rtm = 5
	# temp_frequencies = x[0].keys()
	# frequencies = temp_frequencies[0:3]

	identity = identityTransformation(rtm, frequencies)
	identityDict = identity.returnTransmission()
	exportIdentity(identityDict, fileDirectory, "Computed vals")


main()