'''
Impedance is defined as:
z = p/v

where z is impedance, p is pressure, v is velocity

takes in the transmission table, and outputs impedance
'''

import get_transmission_matrix as gtm
import os
import csv
import math

#define constants
VELOCITY_ONE = [complex(1,0), complex(0,0), complex(0,0), complex(0,0)]
VELOCITY_TWO = [complex(0,0), complex(1,0), complex(0,0), complex(0,0)]
VELOCITY_THREE = [complex(0,0), complex(0,0), complex(1,0), complex(0,0)]
VELOCITY_FOUR = [complex(0,0), complex(0,0), complex(0,0), complex(1,0)]
# VELOCITY_FIVE = [complex(0,0), complex(0,0), complex(0,0), complex(0,0), complex(1,0), complex(0,0)]
# VELOCITY_SIX = [complex(0,0), complex(0,0), complex(0,0), complex(0,0), complex(0,0), complex(1,0)]

VELOCITY_TOT = VELOCITY_ONE + VELOCITY_TWO + VELOCITY_THREE + VELOCITY_FOUR
NUM_CYCLES = 4
# print len(VELOCITY_TOT)
print VELOCITY_TOT

#define file constants
fileDirectory = "Paper/rightFreq independent"
tempOutput = "temp"
filenames = "paperCheck.txt"
listennode = "collimator listennode.txt"
impedanceFile = "collimator impedance"

class acousticImpedance(object):
	def __init__(self, transmissionMatrix, exportFile):
		self.tm = transmissionMatrix
		self.frequencies = self.tm[0].keys()
		self.calcImpedance()
		self.dir = os.path.dirname(__file__)
		self.exportImpedance(exportFile)

	def calcImpedance(self):
		self.impedance = {}
		print self.tm
		for freq in self.frequencies:
			tempList = []
			for i in range(NUM_CYCLES**2):
				if VELOCITY_TOT[i] == 0:
					continue
				tempDict = self.tm[i][freq]
				# val = tempDict[tempDict.keys()[0]]
				tempList.append(tempDict[tempDict.keys()[0]]/VELOCITY_TOT[i]) #appends the log value 
			# print len(tempList)
			self.impedance[freq] = tempList

	def generatefieldnames(self):
		self.fieldnames = ["Frequency"]
		self.matrix_fieldnames = []
		for i in range(NUM_CYCLES):
			tempArr = []
			tempArr.append("Port " + str(i) + " real")
			tempArr.append("Port " + str(i) + " imag")
			self.matrix_fieldnames.append(tempArr)
			self.fieldnames += tempArr
		# print "matrix_fieldnames has dimensions: ", len(self.matrix_fieldnames)
		# print "matrix_fieldnames dim is: ", len(self.matrix_fieldnames[0])

	def generateDict(self, freq, writer):
		# if freq > 1400.0:
			# return
		self.outputDict = {"Frequency": freq}
		for i in range(NUM_CYCLES):
			for j in range(1):
				self.outputDict[self.matrix_fieldnames[i][2*j]] = self.impedance[freq][i].real
				self.outputDict[self.matrix_fieldnames[i][2*j+1]] = self.impedance[freq][i].imag
		writer.writerow(self.outputDict)

	def exportImpedance(self, exportFile):
		self.generatefieldnames()
		outputPath = os.path.join(self.dir, fileDirectory, exportFile + ".csv")
		csvfile = open(outputPath, "w")
		writer = csv.DictWriter(csvfile, fieldnames = self.fieldnames)
		writer.writeheader()
		for freq in self.frequencies:
			self.generateDict(freq, writer)
			# writer.writerow(self.outputDict)


def main():
	tm = gtm.transmissionMatrix(fileDirectory + "/" + filenames, fileDirectory, listennode, tempOutput, 1)
	rtm = tm.returnTransmissionMatrix()
	acousticImpedance(rtm, impedanceFile)

# main()
