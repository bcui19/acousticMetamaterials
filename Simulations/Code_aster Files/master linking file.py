'''
Serves as the massive linking file to link everything together
and does rapid updating of everything to make my life easier to run stuff

So I can update the VELOCITY_VECTOR to match the number of cycles,
the VELOCITY_MATRIX in order to match the input values from the simulation,
and NEW_VELOCITIES to allow for new cross validation
'''

import get_transmission_matrix as gtm
import coalesce_files as coalesce
crossValidation = __import__("cross validation")
checkTransmission = __import__("check_transmission_matrix")
gtw = __import__("get transmission weights")
getIndependent = __import__("Independent Matrix")
import get_identity_matrix as getIndependent_Base #needed to update some stuff for pressure classes lol
validateNodes = __import__("validate node consistency")
calcImpedance = __import__("impedance from transmission matrix")

NUM_CYCLES = 2

ARR_ONE = [1, 0]#, 0, 0]
ARR_TWO = [0, 1]#, 0, 0]
# ARR_THREE = [0, 0, 1, 0]
# ARR_FOUR = [0, 0, 0, 1]
VELOCITY_MATRIX = [ARR_ONE, ARR_TWO]#, ARR_THREE, ARR_FOUR]
VELOCITY_VECTOR = [0] * NUM_CYCLES #Used in finding the independent matrix
NEW_VELOCITIES = [12, 13]#, 4, 3] #used in crossValidation -- needs to be changed to match the length of the velocity

print VELOCITY_MATRIX

#file linked names
filepath = "Paper/Two Cells"#"Paper/rightFreq independent"
simulationFile = "Two cell check.txt"
listennode = "Two Cell listennode.txt"
TESTNO = "Two Cell "
# faceNodes = "cylinder listennode.txt" #Used to make sure the face mesh is tight enough to ensure simulation convergence 
tempOutput = "temp"
coalescedOutput_values = TESTNO + "coalesced transmission values"
identityOutput = TESTNO + "transmission prime values" #outputs transmission prime
weightsOutput = TESTNO + "calculated transmission values" #outputs the transmission matrix values 
impedanceOutput = TESTNO + "calculated impedance" #output impedance CSV

def updateSelf(numCycles, VelocityMatrix, newVelocities):
	global NUM_CYCLES, VELOCITY_MATRIX, VELOCITY_VECTOR, NEW_VELOCITIES
	NUM_CYCLES = numCycles
	VELOCITY_MATRIX = VelocityMatrix
	NEW_VELOCITIES = newVelocities
	VELOCITY_VECTOR = [0] * NUM_CYCLES


def updateFilenames(PATH, SIMULATION, LISTENNODE, TEMP, COALESCED, IDENTITY, WEIGHTS, IMPEDANCE):
	global filepath, simulationFile, listennode, tempOutput, coalescedOutput_values, identityOutput, weightsOutput, impedanceOutput
	filepath = PATH
	simulationFile = SIMULATION
	listennode = LISTENNODE
	tempOutput = TEMP
	coalescedOutput_values = COALESCED
	identityOutput = IDENTITY
	weightsOutput = WEIGHTS
	impedanceOutput = IMPEDANCEc

#updates all of the classes to be consistent with the given parameters
class massiveUpdate(object):
	def __init__(self):
		self.updateClasses()

	def updateClasses(self):
		gtm.updateClass(NUM_CYCLES, VELOCITY_MATRIX)
		gtw.updateClass(NUM_CYCLES, VELOCITY_MATRIX)
		getIndependent.updateClass(NUM_CYCLES, VELOCITY_MATRIX)
		getIndependent_Base.updateClass(NUM_CYCLES)
		crossValidation.updateClass(NUM_CYCLES, VELOCITY_MATRIX, NEW_VELOCITIES)
		calcImpedance.updateClass(NUM_CYCLES)
		coalesce.updateCoalesce(NUM_CYCLES)

#Does a massive validation of the simulation
class validateSimulations(object):
	def __init__(self, transmissionMatrix, transmissionWeights, transmissionPrime):
		self.tm = transmissionMatrix
		self.tw = transmissionWeights
		self.transmissionPrime = transmissionPrime
		self.runValidation()

	def runValidation(self):
		crossValidation.crossValidation(self.tw, self.transmissionPrime, NEW_VELOCITIES)
		# self.validateNodes()

	#validates node consistency across the face of an object to make sure the simulation mesh is tight enough to converge 
	def validateNodes(self):
		listentm = validateNodes.transmissionNodes(filepath + "/" + simulationFile, filepath, faceNodes, tempOutput, 1)
		listennodes = listentm.getListennodes()
		listenrtm = listentm.returnTransmissionMatrix()
		validateNodes.validateNodes(listenrtm, listennodes)

#acts as the glue linking everything together by doing a lot of background running and updatting 
class massiveLinking(object):
	def __init__(self):
		massiveUpdate()

		self.tm = gtm.transmissionMatrix(filepath + "/" + simulationFile, filepath, listennode, tempOutput, 1)
		self.rtm = self.tm.returnTransmissionMatrix()
		self.tw = gtw.getTransmissionWeights(self.rtm).returnWeights()
		self.frequencies = self.rtm[0].keys()
		self.identity = getIndependent.independentMatrix(self.rtm, self.frequencies, VELOCITY_VECTOR)
		self.identityDict = self.identity.returnTransmission()

		validateSimulations(self.rtm, self.tw, self.identityDict) #validates the simulations 

		calcImpedance.calcImpedance(self.tw, impedanceOutput)
		self.exportValues()

	def exportValues(self):
		coalesce.runCoalesce(tempOutput, coalescedOutput_values, filepath)
		getIndependent_Base.exportIdentity(self.tw, filepath, weightsOutput)
		getIndependent_Base.exportIdentity(self.identityDict, filepath, identityOutput)



def main():
	massiveLinking()


main()


