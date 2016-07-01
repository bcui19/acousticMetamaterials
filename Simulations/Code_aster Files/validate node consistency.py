import get_transmission_matrix as gtm
import copy
import os
import csv

#define constants
NUM_CYCLES = 4
DIFF_VAL_REAL = 3e-16
DIFF_VAL_IMAG = 1e-5

class transmissionNodes(gtm.transmissionMatrix):
	def getListennodes(self):
		return self.listenNodes

	def getProperVector(self, presVect, counter, currFreq):
		nodeDict = {}
		for node in presVect:
			key = node.keys()[0] #note there will only be one node 
			# if key != self.listenNodes[counter % NUM_CYCLES]:
				# continue
			# nodeDict[key] = float(node[key][1])/self.inputVelocity #use this to get strictly the real or strictly the imaginary component
			nodeDict[key] = complex(float(node[key][0]), float(node[key][1]))/self.inputVelocity
		return nodeDict


	def dotProduct(self, currFreq, presVect, parity, transMatrix):
		arr = self.getArr(parity)
		tempMatrix = copy.copy(transMatrix)
		counter = 0
		for i in range(len(arr)):
			if arr[i] == 0:
				continue
			nodeDict = self.getProperVector(presVect, counter, currFreq)
			currIndex = copy.copy(tempMatrix[i]) #gets the dictionary for the current transmission matrix

			if currFreq in currIndex:
				currIndex[currFreq] += nodeDict
			else:
				currIndex[currFreq] = nodeDict

			tempMatrix[i] = currIndex
			counter += 1
		return tempMatrix

class validateNodes(object):
	def __init__(self, transmissionMatrix, listenNodes):
		self.tm = transmissionMatrix
		self.listenNodes = listenNodes
		self.validate()

	def validateNode_real(self, currNode, compareNode):
		return 0 if abs(currNode.real - compareNode.real) < DIFF_VAL_REAL else -1

	def validateNode_imag(self, currNode, compareNode):
		return 0 if abs(currNode.imag - compareNode.imag) < DIFF_VAL_IMAG else -1

	def validateFrequency(self, freqDict):
		for freq in freqDict:
			currNode = freqDict[freq][self.listenNodes[0]]
			for i in range(1, len(self.listenNodes)):
				compareNode = freqDict[freq][self.listenNodes[i]] #gets the node to compare to 
				if self.validateNode_real(currNode, compareNode) == -1: #or self.validateNode_imag(currNode, compareNode):
					print "failed at: ", freq
					print "compared to: ", self.listenNodes[0]
					print "at node: ", self.listenNodes[i]
					print "vals were: ", currNode, " and ", compareNode
				# print "vals were: ", currNode, " and ", compareNode

	def validate(self):
		for index in range(len(self.tm)):
			self.validateFrequency(self.tm[index])

def checkNodes(n1, n2):
	for node in n1:
		if node in n2:
			print node, " is here"
		else:
			print node, " is not here"

class exportNodes(object):
	def __init__(self, transmissionMatrix, listenNodes, folderPath, filename):
		self.tm = transmissionMatrix
		self.listenNodes = listenNodes
		self.dir = os.path.dirname(__file__)
		self.path = folderPath
		self.filename = filename
		self.frequencies = self.tm[0].keys()

		self.exportFile()

	def generateFieldnames(self):
		self.fieldnames = ["Frequency"]
		for node in self.listenNodes:
			self.fieldnames.append(node + " real")
			self.fieldnames.append(node + " imag")

	def generateDict(self, freq, counter):
		self.outputDict = {"Frequency": freq}
		for i in range(len(self.listenNodes)):
			self.outputDict[self.fieldnames[2*i + 1]] = self.tm[counter][freq][self.listenNodes[i]].real
			self.outputDict[self.fieldnames[2*i + 2]] = self.tm[counter][freq][self.listenNodes[i]].imag

	def exportFile(self):
		self.generateFieldnames()
		for i in range(NUM_CYCLES**2):
			outputPath = os.path.join(self.dir, self.path, self.filename + str(i) + ".csv")
			csvfile = open(outputPath, "w")
			writer = csv.DictWriter(csvfile, fieldnames = self.fieldnames)
			writer.writeheader()
			for freq in self.frequencies:
				self.generateDict(freq, i)
				writer.writerow(self.outputDict)


def main():
	fileDirectory = "Paper/rightFreq"
	tempOutput = "temp"
	tm = transmissionNodes(fileDirectory + "/paperCheck.txt", fileDirectory, "face nodes.txt", tempOutput, 1)
	rtm = tm.returnTransmissionMatrix()
	frequencies = rtm[0].keys()#[0:1]

	currListennodes = tm.getListennodes()
	# dictListennodes = rtm[1][512.0].keys()
	# checkNodes(currListennodes, dictListennodes)

	validateNodes(rtm, currListennodes)
	exportNodes(rtm, currListennodes, fileDirectory, "pressure for nodes")

	print 5

main()