'''
The code in here takes all of the subdirectories in a folder and tries to 
generate all of the transmission and transmission prime matricies
that are associated with each set of simulations

The code then calls the infinite Calculation module in order to get 
the transmission matrix for a unit cell in the case of an infinite plane e.g.


[P_1] = T[P2]
[V_1]	 [V2]

Note that this transmission matrix dotted with itself should be equal to the identity matrix


'''

#all of the imports
massiveLinking = __import__("master linking file")
infiniteCalc = __import__("Infinite Calculation")
import os
import csv
import copy
import numpy as np
import calcEffectiveParams as calcParams


#file linked names
initSubDir = "pillar_simulations/test" #the initial folder that is looked at for other subfolders for simulations
simulationFile = "paperCheck.txt"
listennode = "collimator listennode.txt"  #"New Dimensions Listennode.txt"
testno = "Paper Actual Size"   #"New Dimensions Unit Cell v1"
# faceNodes = "cylinder listennode.txt" #Used to make sure the face mesh is tight enough to ensure simulation convergence
tempOutput = "temp"

Result_DIR = "pillar_simulations_results/test"
exportFile = Result_DIR + "/density and modulus"

NUM_SIMULATIONS = 4

ARR_ONE = [1, 0, 0, 0]
ARR_TWO = [0, 1, 0, 0]
ARR_THREE = [0, 0, 1, 0]
ARR_FOUR = [0, 0, 0, 1]
VELOCITY_MATRIX = [ARR_ONE, ARR_TWO, ARR_THREE, ARR_FOUR]#, ARR_FIVE, ARR_SIX, ARR_SEVEN, ARR_EIGHT]
VELOCITY_VECTOR = [0] * NUM_SIMULATIONS #Used in finding the independent matrix
NEW_VELOCITIES = [12, 13, 4, 3] #used in crossValidation -- needs to be changed to match the length of the velocity

#simulation constants used for parameter sweeping optimization
AIR_RHO = 1.3
AIR_BULK_MODULUS = 1.42*10**5

#velocity filenames that need to be read
velocities = ["v1,0,0,0", "v0,1,0,0", "v0,0,1,0", "v0,0,0,1"]
output_params = ["S11", "S12", "S21", "S22"]


class massiveMatrixCalculation:
	def __init__(self):
		self.dir = os.path.dirname(__file__)
		self.outputDir = os.path.join(self.dir, Result_DIR)

		#get the subdirectories
		self.failure = 0
		self.subdirs = next(os.walk(initSubDir))[1]
		#self.subdirs = ['unit_cell_H0.005000_L0.002000']

		self.concatenatedList = []
		self.rhoResu = []
		self.lambdaResu = []
		self.LList = []
		self.HList = []
                self.RList = []
                self.VList = []

                
                self.runCalculations()

		self.writeConcatenatedOutput()

		self.displayResu()

	#called to get the nearest density/modulus depending upon the input index
	def nearestDensity(self, currVal, dBool, index):
		diffVal = abs(currVal - AIR_RHO if dBool == 1 else currVal - AIR_BULK_MODULUS)
		currNeighborNum = self.numNeighbors_Density if dBool == 1 else self.numNeighbors_Modulus
		currNeighbors = self.nearestNeighbors_Density if dBool == 1 else self.nearestNeighbors_Modulus
		maxDiff = self.maxDiff_Density if dBool == 1 else self.maxDiff_Modulus
		minDiff = self.minDiff_Density if dBool == 1 else self.minDiff_Modulus



		if diffVal < maxDiff or currNeighbors < self.maxNeighbors:
			# print "in if statement" # I should comment this out later
			returnDiff = diffVal
			return (diffVal, True)
		return (diffVal, False)


	#displays the final results of the simulations
	#uses a nearest neighbor approach to get the optimal simulations
	def displayResu(self):
		#nearest neighbor features

		self.nearestNeighbors_Density = []
		self.nearestNeighbors_Modulus = []
		self.numNeighbors_Density = 0
		self.numNeighbors_Modulus = 0
		self.maxNeighbors = 6

		#diffInitializers
		maxVal = -100
		minVal = 100
		self.minDiff_Density = 0
		self.minDiff_Modulus = 0
		self.maxDiff_Density = 10000000000
		self.maxDiff_Modulus = 10000000000

		#indexInitilization
		diffIndex = 0
		maxIndex = 0
		minIndex = 0

		nearestVal_Count = 0
		for i in range(len(self.rhoResu)):
			currVal = self.rhoResu[i]
			if currVal > maxVal:
				maxVal = currVal
				maxIndex = i
			if currVal < minVal:
				minVal = currVal
				minIndex = i

			nearestVal = self.nearestDensity(currVal, 1, i)
			#do updating here
			if nearestVal[1]:
				self.minDiff_Density = nearestVal[0] if nearestVal[0] < self.minDiff_Density else self.minDiff_Density
				self.maxDiff_Density = nearestVal[0] if nearestVal[0] > self.maxDiff_Density else self.maxDiff_Density
				if self.numNeighbors_Density == self.maxNeighbors:
					self.nearestNeighbors_Density.pop(self.maxNeighbors-1)
				resuTuple = (nearestVal[0], currVal, i)
				self.nearestNeighbors_Density.append(resuTuple)
				self.nearestNeighbors_Density = sorted(self.nearestNeighbors_Density, key = lambda currVal : currVal[0])

				if self.numNeighbors_Density < self.maxNeighbors:
					self.numNeighbors_Density += 1

			currVal = self.lambdaResu[i]
			
			#update modulus
			nearestVal = self.nearestDensity(currVal, 0, i)
			if nearestVal[1]:
				nearestVal_Count += 1
				self.minDiff_Modulus = nearestVal[0] if nearestVal[0] < self.minDiff_Modulus else self.minDiff_Modulus
				self.maxDiff_Modulus = nearestVal[0] if nearestVal[0] > self.maxDiff_Modulus else self.maxDiff_Modulus
				if self.numNeighbors_Modulus == self.maxNeighbors:
					self.nearestNeighbors_Modulus.pop(self.maxNeighbors-1)
				resuTuple = (nearestVal[0], currVal, i)
				self.nearestNeighbors_Modulus.append(resuTuple)
				self.nearestNeighbors_Modulus = sorted(self.nearestNeighbors_Modulus, key = lambda currVal: currVal[0])

				if self.numNeighbors_Modulus < self.maxNeighbors:
					self.numNeighbors_Modulus += 1

		print "maxVal is: %f, maxIndex is: %d" %(maxVal, maxIndex)
		print "minVal is: %f, minIndex is: %d" %(minVal, minIndex)
		# print "diffRho is: %f" %(self.rhoResu[diffIndex])
		# print "minDiff is: %f, diffIndex is: %d" %(minDiff, diffIndex)

		print "maxH is: %f, maxL is: %f" %(self.HList[maxIndex], self.LList[maxIndex])
		print "minH is: %f, minL is: %f" %(self.HList[minIndex], self.LList[minIndex])
		# print "diffH is: %f, diffL is: %f" %(self.HList[diffIndex], self.LList[diffIndex])

		for i in range(len(self.nearestNeighbors_Density)):
			currTuple = self.nearestNeighbors_Density[i]
                        print ("index is: %d, diff is: %f, rho val is: %f H is: %f, L is: %f,R is: %f, V is: %d, lambda is: %f"
			%(currTuple[2], currTuple[0], currTuple[1], self.HList[currTuple[2]], self.LList[currTuple[2]], self.RList[currTuple[2]], self.VList[currTuple[2]], self.lambdaResu[currTuple[2]]))
			currTuple = self.nearestNeighbors_Modulus[i]
                        print ("index is: %d, diff is: %f, modulus val is: %f H is: %f, L is: %f,R is: %s, V is: %d, rho is: %f\n"
			%(currTuple[2], currTuple[0], currTuple[1], self.HList[currTuple[2]], self.LList[currTuple[2]],self.RList[currTuple[2]], self.VList[currTuple[2]], self.rhoResu[currTuple[2]]))

		print "the number of failures was: ", self.failure
		print "number of simulations is: ", len(self.subdirs)
		print "nearestVal count is: ", nearestVal_Count
		print "correct simulations are: ", len(self.RList)

	#runs the calculations for the transmission, transmission prime and infinite calculation matrix
	def runCalculations(self):
		self.correctSim = []
		for subdir in self.subdirs:
			try:
				self.runSingleCalculation(subdir)
			except IOError as e:
				print "I think this is a caching error"

	#runs a single calculation 
	def runSingleCalculation(self, subdir):
		try:
		    self.massiveUpdates(subdir)
		    linkedData = massiveLinking.massiveLinking()
		    self.frequencies = linkedData.returnWeights().keys()
		    self.rtm = linkedData.returnTransmissionMatrix()
		    infinitePlane = infiniteCalc.infiniteCalc(linkedData.returnWeights(), self.frequencies)


		    infiniteResult = infinitePlane.returnResult()
		    tprimecalc = infiniteCalc.calculateTransmissionMatrix(infiniteResult, self.frequencies)
		    self.tprime = tprimecalc.returnTPrime()



		    self.writeSingleResultCSV(subdir)
		    self.writeBinaryFile(subdir)

		    curTuple = (self.tprime, subdir)
		    self.concatenatedList.append(copy.copy(curTuple))
		# self.validateMatricies(subdir) #call this code for validation if you want
		except IndexError as e:
			print "index error in massive linking most likely"

		try:
			self.extractParams(Result_DIR, subdir)
		except AttributeError as e:
			print "no attribute, something went wrong"
		except IOError as e:
			print "code aster did something wrong"

		self.correctSim.append(subdir)
		# except IndexError as e:
		# 	self.failure += 1
		# 	print "There's an index error in the transmission matrix"
		# except IOError as e:
		# 	self.failure += 1
		# 	print "There was an IOError, not sure why this happened"
		# 	return False



	#does the  necessary updates for the current simulation set
	def massiveUpdates(self, subdir):
		self.createSimFilenames(subdir)
		currDir = os.path.join(self.dir, initSubDir, subdir)
		currListennode = subdir + ".listennode"
		self.testno = subdir + " calculation"

		infiniteCalc.updateFilenames(FILEPATH = currDir, SIMULATIONFILE = "simulation files.txt", LISTENNODE = currListennode, TESTNO = subdir + " calculation")
		self.updateFilenames()
		massiveLinking.updateSelf(numCycles = NUM_SIMULATIONS, velocityMatrix = VELOCITY_MATRIX, newVelocities = NEW_VELOCITIES)
		massiveLinking.updateFilenames(currDir, "simulation files.txt", currListennode, tempOutput, self.coalescedOutput, self.identityOutput, self.weightsOutput, self.impedanceOutput)


	def updateFilenames(self):
		self.coalescedOutput = self.testno + "coalesced transmission values"
		self.identityOutput = self.testno + "transmission prime values"
		self.weightsOutput = self.testno + "calculated transmission values"
		self.impedanceOutput = self.testno + "calculated impedance"

	#creates the simulation filenames and locations
	def createSimFilenames(self, subdir):
		fileExport = ""
		for i in range(NUM_SIMULATIONS):
			fileExport += os.path.join(initSubDir, subdir, subdir + velocities[i] +".resu\n")


		filename = "simulation files.txt"
		currDir = os.path.join(self.dir, initSubDir, subdir)

		outputFile = os.path.join(currDir, filename)

		# print outputFile
		of = open(outputFile, "w")
		of.write(fileExport)

	#outputs the transmission matrix as a binary file
	def writeBinaryFile(self, subdir):
		outputfile = os.path.join(self.outputDir, subdir)
		try:
			np.save(outputfile, self.tprime[10000.0])
		except KeyError as e:
			print "there is a key error"

	#creates a dictionray to be used in outputting a CSV file
	def createSingleResultDict(self, freq):
		self.currDict = {}
		for i in range(len(self.tprime[freq])*2):
			self.currDict[output_params[i]] = self.tprime[freq][0 if i < 2 else 1][0 if i == 0 or i == 2 else 1]
			self.currDict["freq"] = freq

	#outputs a single transmission matrix as a CSV
	def writeSingleResultCSV(self, subdir):
		if not os.path.exists(self.outputDir):
			os.makedirs(self.outputDir)
		outputfile = os.path.join(self.outputDir, subdir + ".csv")
		csvfile = open(outputfile, "w")
		fieldnames = ["freq", "S11", "S12", "S21", "S22"]
		writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
		writer.writeheader()
		for freq in self.tprime:
			self.createSingleResultDict(freq)
			writer.writerow(self.currDict)

	#used to output the infinite transmission matrix as a CSV file
	def createCurrResultDict(self, currTuple, csvWriter):
		self.tempDict = {"geometry" : currTuple[1]}
		currDict = currTuple[0]
		for freq in currDict:
			self.tempDict["freq"] = freq
			currArr = currDict[freq]
			for i in range(len(currArr)*2):
				self.tempDict[output_params[i]] = currArr[0 if i == 0 or i == 2 else 1]
			csvWriter.writerow(self.tempDict)

	#outputs all of the transmission matrix as a CSV file
	def writeConcatenatedOutput(self):
		if not os.path.exists(self.outputDir):
			os.makedirs(self.outputDir)

		outputfile = os.path.join(self.outputDir, "Coalesced values.csv")
		csvfile = open(outputfile, "w")
		fieldnames = ["geometry", "freq", "S11", "S12", "S21", "S22"]
		writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
		writer.writeheader()
		for currTuple in self.concatenatedList:
			self.createCurrResultDict(currTuple, writer)

	#just prints out the matrix time by itself for each frequency
	#in the infinite plane case, the dot product of the matrix and itself should be the identity matrix
	def validateMatricies(self, subdir):
		print "current subdir is: ", subdir
		for matrix in self.concatenatedList:
			currDict = matrix[0]
			for freq in currDict:
				currMatrix = currDict[freq]
				print "for freq: ", freq
				print "the product of the matrix and itself is: "
				print np.dot(currMatrix, currMatrix)

	#code called to extract density and bulk modulus out of the transmission matrix
	def extractParams(self, subdir, filename):
		calcParams.updateClass(subdir)
		self.dir = os.path.dirname(__file__)
		filepath = os.path.join(self.dir, filename + ".npy")
		paramCalc = calcParams.effectiveParamsEval(filepath, exportFile)
		self.rhoResu.append(paramCalc.returnRho())
		self.lambdaResu.append(paramCalc.returnLambda())
		self.LList.append(paramCalc.returnL())
		self.HList.append(paramCalc.returnH())
                self.RList.append(paramCalc.R)
                self.VList.append(paramCalc.V)
                

if __name__ == "__main__":
	massiveMatrixCalculation()







