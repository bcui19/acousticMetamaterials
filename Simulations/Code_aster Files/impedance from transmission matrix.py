'''
From: http://www.cs.columbia.edu/cg/lego/acoustic-voxels-siggraph-2016-li-et-al-compressed.pdf

calculates impedance based upon the transmission matrix:

[p0]	= 	[T11  T12][V0]
[p1]		[T21  T22][V1]

Z = (T11 + T12 * T21 - T11 * T22)/(1- T22)

Currently only coded to work for a two port system
'''


import get_transmission_matrix as gtm
gtw = __import__("get transmission weights")
import os
import csv
import math


# VELOCITY_TOT = VELOCITY_ONE + VELOCITY_TWO + VELOCITY_THREE + VELOCITY_FOUR
NUM_CYCLES = 2
# print len(VELOCITY_TOT)
# print VELOCITY_TOT

#define file constants
fileDirectory = "code aster check/cylinder d10cm L1m"
tempOutput = "temp"
filenames = "cylinder check.txt"
listennode = "cylinder listennode.txt"
impedanceFile = "cylinder calculated impedance"

def updateClass(numCylces):
	global NUM_CYCLES
	NUM_CYCLES = numCylces

class calcImpedance(object):
	def __init__(self, weights, exportFile):
		self.weights = weights
		self.frequencies = weights.keys()
		self.dir = os.path.dirname(__file__)
		self.exportFile = exportFile
		self.getImpedance()
		self.outputImpedance()

	def getImpedance(self):
		self.impedance = {}
		for freq in self.frequencies:
			self.calculate(freq)
			# if abs(self.tempImpedance) > 1000:
				# continue 
			self.impedance[freq] = self.tempImpedance

	def calculate(self, freq):
		T11 = self.weights[freq][0][0]
		T12 = self.weights[freq][0][1]
		T21 = self.weights[freq][1][0]
		T22 = self.weights[freq][1][1]
		self.tempImpedance = (T11 + T12 * T21 - T11 * T22)/ (1- T22)

	def generateFieldnames(self):
		self.fieldnames = ["Frequency", "Port1 Real", "Port1 Imag"]

	def generateDict(self, freq, writer):
		self.outputDict = {"Frequency": freq}
		self.outputDict[self.fieldnames[1]] = self.impedance[freq].real
		self.outputDict[self.fieldnames[2]] = self.impedance[freq].imag
		writer.writerow(self.outputDict)

	def outputImpedance(self):
		self.generateFieldnames()
		ouputPath = os.path.join(self.dir, fileDirectory, self.exportFile + ".csv")
		csvfile = open(ouputPath, "w")
		writer = csv.DictWriter(csvfile, fieldnames = self.fieldnames)
		writer.writeheader()
		for freq in self.impedance:
			self.generateDict(freq, writer)


def initialize():
	tm = gtm.transmissionMatrix(fileDirectory + "/" + filenames, fileDirectory, listennode, tempOutput, 1)
	rtm = tm.returnTransmissionMatrix()
	tw = gtw.getTransmissionWeights(rtm)
	return tw.returnWeights()

def main():
	weights = initialize()
	calcImpedance(weights, impedanceFile)

# main()