cppProcessing = __import__("cpp processing")

#defines the number of simulations run for confirmation
#This number should match the number of ports to get a stable solution
#to the linear algebra system 
NUM_CYCLES = 4

ARR_ONE = [5, 0, 0, 0]
ARR_TWO = [0, 5, 0, 0]
ARR_THREE = [0, 0, 5, 0]
ARR_FOUR = [0, 0, 0, 5]
VELOCITY_MATRIX = [ARR_ONE, ARR_TWO, ARR_THREE, ARR_FOUR]

#including file constants
FILEPATH = "Paper/Two Cells Four Ports"
FILENAME = "simulation names csv.txt"
WEIGHTS_OUTPUT = "Two cells 4 Ports calculated weights"
IDENTITY_OUTPUT = "calculated transmission prime output"
PORTFILE = "ports.txt"



if __name__ == "__main__":
	cppProcessing.updateClass(NUM_CYCLES, VELOCITY_MATRIX)
	cppProcessing.runProcessing()