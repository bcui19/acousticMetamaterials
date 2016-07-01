import get_identity_matrix as gim
import get_transmission_matrix as gtm
import numpy as np

#define constants
NUM_CYCLES = 4
VELOCITY_SOLUTION_MATRIX = [0] * NUM_CYCLES
fileDirectory = "Paper/rightFreq independent"


class independentMatrix(gim.identityTransformation):

	def getOrigMatrix(self, freq):
		arrStor = []
		for i in range(NUM_CYCLES):
			tempArr = [0]*NUM_CYCLES
			press2 = self.tm[NUM_CYCLES + i][freq]
			tempArr[0] = press2[press2.keys()[0]] #there will only be one key
			press4 = self.tm[NUM_CYCLES*3 + i][freq]
			tempArr[2] = press4[press4.keys()[0]]
			
			tempArr[1] = complex(1, 0) if i == 1 else complex(0, 0)
			if i == 2:
				tempArr[1] = complex(1,0)
				tempArr[3] = complex(1,0) 

			arrStor.append(tempArr)
		# print "arrStor is: ", arrStor
		return arrStor

	def getVelocityMatrix(self, index, freq):
		origMatrix = self.getOrigMatrix(freq)
		solutionMatrix = VELOCITY_SOLUTION_MATRIX[:]
		solutionMatrix[index] = complex(1,0)
		if index == 2:
			solutionMatrix[1] = complex(1,0)
			solutionMatrix[3] = complex(1,0)
		# print "solution Matrix is: ", solutionMatrix
		return np.linalg.solve(origMatrix, solutionMatrix)

def initialize():
	tempOutput = "temp"
	tm = gtm.transmissionMatrix(fileDirectory + "/paperCheck.txt", fileDirectory, "collimator listennode.txt", tempOutput, 1)
	rtm = tm.returnTransmissionMatrix()
	frequencies = rtm[0].keys()
	# coalesce.runCoalesce(tempOutput, "coalesced", fileDirectory)
	# temp_frequencies = x[0].keys()
	# frequencies = temp_frequencies[:]

	# identity = gim.identityTransformation(rtm, frequencies)
	# identityDict = identity.returnTransmission()
	# exportIdentity(identityDict, fileDirectory, "Computed identity vals")
	return rtm, frequencies

def main():
	transmissionMatrix, frequencies = initialize()
	# tempFreq = frequencies[0:1]
	identity = independentMatrix(transmissionMatrix, frequencies)
	identityDict = identity.returnTransmission()
	gim.exportIdentity(identityDict, fileDirectory, "Computed identity vals")
	
main()