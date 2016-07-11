import get_transmission_matrix as gtm
import coalesce_files as coalesce
crossValidation = __import__("cross validation")
checkTransmission = __import__("check_transmission_matrix")
gtw = __import__("get transmission weights")
getIndependent = __import__("Independent Matrix")
import get_identity_matrix as getIndependent_Base #needed to update some stuff for pressure classes lol
validateNodes = __import__("validate node consistency")

NUM_CYCLES = 2

ARR_ONE = [1, 0]#, 0, 0]
ARR_TWO = [0, 1]#, 1, 1]
# ARR_THREE = [0, 1, 0, 1]
# ARR_FOUR = [0, 0, 1, 1]
VELOCITY_MATRIX = [ARR_ONE, ARR_TWO]#, ARR_THREE, ARR_FOUR]
VELOCITY_VECTOR = [0] * NUM_CYCLES

#file linked names
filepath = "code aster check/cylinder d10cm L1m"#"Paper/rightFreq independent"
simulationFile = "cylinder check.txt"
listennode = "cylinder listennode.txt"
tempOutput = "temp"

#updates all of the classes 
class massiveUpdate(object):
	def __init__(self):
		self.updateClasses()

	def updateClasses(self):
		gtm.updateClass(NUM_CYCLES, VELOCITY_MATRIX)
		gtw.updateClass(NUM_CYCLES, VELOCITY_MATRIX)
		getIndependent.updateClass(NUM_CYCLES, VELOCITY_MATRIX)
		getIndependent_Base.updateClass(NUM_CYCLES)
		crossValidation.updateClass(NUM_CYCLES, VELOCITY_MATRIX)


class validateSimulations(object):
	def __init__(self, transmissionMatrix, transmissionWeights, transmissionPrime):
		self.tm = transmissionMatrix
		self.tw = transmissionWeights
		self.transmissionPrime = transmissionPrime
		self.runValidation()

	def runValidation(self):
		crossValidation.crossValidation(self.tw, self.transmissionPrime, VELOCITY_VECTOR)

class massiveLinking(object):
	def __init__(self):
		massiveUpdate()
		self.tm = gtm.transmissionMatrix(filepath + "/" + simulationFile, filepath, listennode, tempOutput, 1)
		self.rtm = self.tm.returnTransmissionMatrix()
		self.tw = gtw.getTransmissionWeights(self.rtm).returnWeights()
		self.frequencies = self.rtm[0].keys()
		self.identity = getIndependent.independentMatrix(self.rtm, self.frequencies, VELOCITY_VECTOR)
		self.identityDict = self.identity.returnTransmission()
		# print self.identity.returnTransmission()

		validateSimulations(self.rtm, self.tw, self.identityDict) #validates the simulations 


def main():
	massiveLinking()
	# massiveUpdate()
	# rtm = gtm.transmissionMatrix(filepath + "/" + simulationFile, filepath, listennode, tempOutput, 1).returnTransmissionMatrix()
	# tw = gtw.getTransmissionWeights(rtm).returnWeights
	# frequencies = rtm[0].keys()
	# identityDict = getIndependent.independentMatrix(rtm, frequencies, VELOCITY_VECTOR)
	# validateSimulations(rtm, tw, )



main()


