massiveLinking = __import__("master linking file")

NUM_CYCLES = 4 #represents the nnumber of simulations 

ARR_ONE = [1, 0, 0, 0]
ARR_TWO = [0, 1, 0, 0]
ARR_THREE = [0, 0, 1, 0]
ARR_FOUR = [0, 0, 0, 1]
VELOCITY_MATRIX = [ARR_ONE, ARR_TWO]#, ARR_THREE, ARR_FOUR]
VELOCITY_VECTOR = [0] * NUM_CYCLES #Used in finding the independent matrix
NEW_VELOCITIES = [12, 13, 4, 3] #used in crossValidation -- needs to be changed to match the length of the velocity

# print VELOCITY_MATRIX

#file linked names
filepath = "New Dimensions/New Dimensions v1"#"Paper/rightFreq independent"
simulationFile = "New Dimensions Check v1.txt"
listennode = "New Dimensions Listennode.txt"
TESTNO = "New Dimensions Unit Cell v1"
# faceNodes = "cylinder listennode.txt" #Used to make sure the face mesh is tight enough to ensure simulation convergence 
tempOutput = "temp"
coalescedOutput_values = TESTNO + "coalesced transmission values"
identityOutput = TESTNO + "transmission prime values" #outputs transmission prime
weightsOutput = TESTNO + "calculated transmission values" #outputs the transmission matrix values 
impedanceOutput = TESTNO + "calculated impedance" #output impedance CSV



if __name__ == "__main__":
	massiveLinking.updateSelf(numCycles = NUM_CYCLES, velocityMatrix = VELOCITY_MATRIX, newVelocities = NEW_VELOCITIES)
	massiveLinking.updateFilenames(filepath, simulationFile, listennode, tempOutput, coalescedOutput_values, identityOutput, weightsOutput, impedanceOutput)
	massiveLinking.massiveLinking()
	print 5