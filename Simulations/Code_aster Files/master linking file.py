'''
Serves as the massive linking file to link everything together
and does rapid updating of everything to make my life easier to run stuff

So I can update the VELOCITY_VECTOR to match the number of cycles,
the VELOCITY_MATRIX in order to match the input values from the simulation,
and NEW_VELOCITIES to allow for new cross validation

Generally by updating the constants located in the file it will result update the instsance of
the imported modules 

Generally the ports are numbered as follows:
    	 3
        ||
	2  =  =  4
		||
	 	 1

I think the ordering of ports doesn't matter, just the lists that make up the VELOCITY_MATRIX
need to align with how the simulations are read from the 'simulationFile'

The transmission matrix refers to:

[P0]		 [V0]
[P1]	=	T[V1]
[P2]		 [V3]
[P3]		 [V4]

The transmission prime matrix refers to:

[P0]		  [P1]
[V0]	=	T`[V1]
[P2]		  [P3]
[V2]		  [V3]

'''
#all the imports needed, all of these are other modules created
import get_transmission_matrix as gtm
import coalesce_files as coalesce
crossValidation = __import__("cross validation")
checkTransmission = __import__("check_transmission_matrix")
gtw = __import__("get transmission weights")
getIndependent = __import__("Independent Matrix")
import get_identity_matrix as getIndependent_Base #needed to update some stuff for pressure classes lol
validateNodes = __import__("validate node consistency")
calcImpedance = __import__("impedance from transmission matrix")

NUM_CYCLES = 4 #represents the nnumber of simulations 

#the following represent the boundary conditions at each of the ports
#for a given simulation
ARR_ONE = [1, 0, 0, 0] #represents the simulation case of 
ARR_TWO = [0, 1, 0, 0]
ARR_THREE = [0, 0, 1, 0]
ARR_FOUR = [0, 0, 0, 1]

#A matrix that consists of the velocity simulation parameters
#each row consists of the velocity parameters for a given simulation
VELOCITY_MATRIX = [ARR_ONE, ARR_TWO, ARR_THREE, ARR_FOUR]
#Initializing a vector of 0's that matches the length of the number of simulations
#used in the Independent Matrix module
VELOCITY_VECTOR = [0] * NUM_CYCLES
#used in crossValidation -- its length needs to match the number of simulations
NEW_VELOCITIES = [12, 13, 4, 3] 


#define filenames

filepath = "paper/Paper Copy Actual Size" #represents the directory where the simulations are located
simulationFile = "paperCheck.txt" #txt file that is read containing the simulation .resu files in order
listennode = "collimator listennode.txt" #the listennode file
TESTNO = "Paper Copy" #generic file placeholder to add to 

#currently commented out because I couldn't figure out a clean way to get all of the listennodes
# faceNodes = "cylinder listennode.txt" #Used to make sure the face mesh is tight enough to ensure simulation convergence 
tempOutput = "temp"
coalescedOutput_values = TESTNO + "coalesced transmission values" #takes all of the transmission values (real and imaginary) and puts them into a file
identityOutput = TESTNO + "transmission prime values" #outputs transmission prime
weightsOutput = TESTNO + "calculated transmission values" #outputs the transmission matrix values 
impedanceOutput = TESTNO + "calculated impedance" #output impedance CSV

#call in other modules to update the constants in this file
def updateSelf(numCycles = NUM_CYCLES, velocityMatrix = VELOCITY_MATRIX, newVelocities = NEW_VELOCITIES):
	global NUM_CYCLES, VELOCITY_MATRIX, VELOCITY_VECTOR, NEW_VELOCITIES
	NUM_CYCLES = numCycles
	VELOCITY_MATRIX = velocityMatrix
	NEW_VELOCITIES = newVelocities
	VELOCITY_VECTOR = [0] * NUM_CYCLES

#call in other modules to update the filenames in this file
def updateFilenames(PATH, SIMULATION, LISTENNODE, TEMP, COALESCED, IDENTITY, WEIGHTS, IMPEDANCE):
	global filepath, simulationFile, listennode, tempOutput, coalescedOutput_values, identityOutput, weightsOutput, impedanceOutput
	filepath = PATH
	simulationFile = SIMULATION
	listennode = LISTENNODE
	tempOutput = TEMP
	coalescedOutput_values = COALESCED
	identityOutput = IDENTITY
	weightsOutput = WEIGHTS
	impedanceOutput = IMPEDANCE

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

#This class does validation of the simulation
class validateSimulations(object):
	def __init__(self, transmissionMatrix, transmissionWeights, transmissionPrime):
		self.tm = transmissionMatrix
		self.tw = transmissionWeights
		self.transmissionPrime = transmissionPrime
		self.runValidation()

	def runValidation(self):
		#cross validation between the transmission matrix and transmission prime matrix using arbitrarily put in velocities
		#makes sure the transmission prime matrix really is just a linear transformation of the transmission matrix
		crossValidation.crossValidation(self.tw, self.transmissionPrime, NEW_VELOCITIES)
		#For validate nodes need to have the right listennode
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

		self.tm = gtm.transmissionMatrix(filepath + "/" + simulationFile, filepath, listennode, tempOutput, 1) #reference to the transmissionMatrix class
		self.rtm = self.tm.returnTransmissionMatrix() #gets a proper 

		# print self.rtm[1]
		self.twf = gtw.getTransmissionWeights(self.rtm) #class variable 
		self.twf.averageWeights() #averages the weights so on infinite calculation gets a good result
		self.tw = self.twf.weights #gets the actual weights of the transmission matrix
		# print self.tw
		self.frequencies = self.rtm[0].keys() #frequencies of the simulation 

		self.identity = getIndependent.independentMatrix(self.rtm, self.frequencies, VELOCITY_VECTOR)
		self.identityDict = self.identity.returnTransmission()

		# validateSimulations(self.rtm, self.tw, self.identityDict) #validates the simulations #right now the validation code doesn't work because I forcefully took the averages

		calcImpedance.calcImpedance(self.tw, impedanceOutput) #calculates the impedance as seen in the siggraph paper
		self.exportValues()

		# print self.tw

	#exports everything
	def exportValues(self):
		coalesce.runCoalesce(tempOutput, coalescedOutput_values, filepath)
		getIndependent_Base.exportIdentity(self.tw, filepath, weightsOutput)
		getIndependent_Base.exportIdentity(self.identityDict, filepath, identityOutput)

	def returnTransmissionMatrix(self):
		return self.rtm

	def returnWeights(self):
		return self.tw



def main():
	linked = massiveLinking()


if __name__ == "__main__":
	main()


