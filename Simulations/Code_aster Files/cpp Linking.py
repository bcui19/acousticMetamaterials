import subprocess
linking = __import__("master linking file")

# NUM_CY

NUM_CYCLES = 4

ARR_ONE = [1, 0, 0, 0]
ARR_TWO = [0, 1, 1, 1]
ARR_THREE = [0, 1, 0, 1]
ARR_FOUR = [0, 0, 1, 1]
VELOCITY_MATRIX = [ARR_ONE, ARR_TWO, ARR_THREE, ARR_FOUR]
VELOCITY_VECTOR = [0] * NUM_CYCLES #Used in finding the independent matrix
NEW_VELOCITIES = [12, 13, 4, 3] #used in crossValidation -- needs to be changed to match the length of the velocity

#file linked names
filepath = "Paper/rightFreq"#"Paper/rightFreq independent"
simulationFile = "paperCheck.txt"
listennode = "collimator listennode.txt"
# faceNodes = "cylinder listennode.txt" #Used to make sure the face mesh is tight enough to ensure simulation convergence 
tempOutput = "temp"
coalescedOutput_values = "coalesced transmission values"
identityOutput = "transmission prime values" #outputs transmission prime
weightsOutput = "calculated transmission values" #outputs the transmission matrix values 
impedanceOutput = "calculated impedance" #output impedance CSV

class updateLinking(object):
	def __init__(self):
		self.updateLinks()

	def updateLinks(self):
		linking.updateSelf(NUM_CYCLES, VELOCITY_MATRIX, NEW_VELOCITIES)
		linking.updateFilenames(filepath, simulationFile, listennode, tempOutput, 
		coalescedOutput_values, identityOutput, weightsOutput, impedanceOutput)



def main():
	updateLinking()

main()