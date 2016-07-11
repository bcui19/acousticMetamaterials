import os 
import copy
import numpy as np
import cmath
import csv
import coalesce_files as coalesce
import get_transmission_matrix as gtm


#Define constants
NUM_CYCLES = 4
# VELOCITY_SOLUTION_MATRIX = [0] * NUM_CYCLES

def updateClass(numCycles):
	global NUM_CYCLES
	NUM_CYCLES = numCycles

class identityTransformation(object):
	def __init__(self, transmissionMatrix, frequencies, velocityMatrix):
		self.tm = transmissionMatrix
		self.velocityMatrix = velocityMatrix
		# print "transmission matrix is: ", len(self.tm)
		self.freq = frequencies
		self.getTransmission()
		self.simplifyIdentity()
		# self.getPressureMatrix(0, 512.0)

	def getOrigMatrix(self, freq):
		arrStor = []
		for i in range(NUM_CYCLES):
			tempArr = [0]*NUM_CYCLES
			press2 = self.tm[NUM_CYCLES + i][freq]
			tempArr[0] = press2[press2.keys()[0]] #there will only be one key
			press4 = self.tm[NUM_CYCLES*3 + i][freq]
			tempArr[2] = press4[press4.keys()[0]]
			
			tempArr[1] = complex(1, 0) if i == 1 else complex(0, 0)
			tempArr[3] = complex(1, 0) if i == 3 else complex(0, 0) 

			arrStor.append(tempArr)
		# print "arrStor is: ", arrStor
		return arrStor

	def getSolMatrix(self, index, freq):
		solArr = []
		for i in range(NUM_CYCLES):
			tempDict = self.tm[NUM_CYCLES * index + i][freq]
			# print "indexing is: ", NUM_CYCLES * index + i
			solArr.append(tempDict[tempDict.keys()[0]])
		return solArr

	def getPressureMatrix(self, index, freq):
		origMatrix = self.getOrigMatrix(freq)
		pressureVect = self.getSolMatrix(index, freq)
		# print "Pressure Vect is: ", pressureVect
		# print "Orig Matrix is: ", origMatrix
		return np.linalg.solve(origMatrix, pressureVect)

	def getVelocityMatrix(self, index, freq):
		origMatrix = self.getOrigMatrix(freq)
		solutionMatrix = self.velocityMatrix[:]
		solutionMatrix[index] = complex(1,0)
		# print "solution Matrix is: ", solutionMatrix
		return np.linalg.solve(origMatrix, solutionMatrix)

	def getTransmission(self):
		self.identityDict = {}
		for currFreq in self.freq:
			# if currFreq == 2528.0:
				# continue
			solArr = []
			for j in [0,2]:
				presSol = self.getPressureMatrix(j, currFreq)
				velSol = self.getVelocityMatrix(j, currFreq)
				# print "pressure Solution is: ", presSol
				# print "Velocity Solution is: ", velSol
				solArr.append(presSol)
				solArr.append(velSol)

			self.identityDict[currFreq] = solArr

	def reduceArr(self, currArr):
		for i in range(len(currArr)):
			for j in range(len(currArr)):
				if i == j:
					currArr[i][j] -= 1
		return currArr

	def simplifyIdentity(self):
		for freq in self.identityDict:
			currArr = self.identityDict[freq]
			# currArr = self.reduceArr(currArr)
			self.identityDict[freq] = currArr

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
		for freq in self.frequencies:
			self.generateDict(freq)
			writer.writerow(self.outputDict)


def main():
	fileDirectory = "Paper/rightFreq"
	tempOutput = "temp"
	tm = gtm.transmissionMatrix(fileDirectory + "/paperCheck.txt", fileDirectory, "collimator listennode.txt", tempOutput, 1)
	rtm = tm.returnTransmissionMatrix()
	frequencies = rtm[0].keys()[0:1]
	# coalesce.runCoalesce(tempOutput, "coalesced", fileDirectory)

	# temp_frequencies = x[0].keys()
	# frequencies = temp_frequencies[:]
	velocityVector = [0] * NUM_CYCLES

	identity = identityTransformation(rtm, frequencies, velocityVector)
	identityDict = identity.returnTransmission()
	# print identityDict[25000.0][2]
	exportIdentity(identityDict, fileDirectory, "Computed identity vals")


# main()