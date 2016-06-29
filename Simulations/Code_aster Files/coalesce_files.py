#separate file that will be run to concatonate files

import os
import csv
import cmath

#define constants
NUM_FILES = 16
PATH = "Paper Copy Actual Size"


def coalesce(filenames, path):
	returnList = []
	dir = os.path.dirname(__file__)
	for i in range(len(filenames)):
		freqList = []
		tempList = []
		tempPath = os.path.join(dir, path, filenames[i])
		csvfile = open(tempPath, "r")
		reader = csv.DictReader(csvfile)
		for row in reader:
			freqList.append(float(row["Frequency"]))
			tempList.append(complex(float(row["Real"]), float(row["Imaginary"])))
		returnList.append(tempList)
	return returnList, freqList

def generateFieldnames(fieldname):
	tempArr = ["Frequency"]
	for i in range(NUM_FILES):
		tempArr.append(fieldname + str(i) + " real")
		tempArr.append(fieldname + str(i) + " imag")
	return tempArr

def rewriteData(coalescedData, freqList, path, outputName):
	outputfile = os.path.join(os.path.dirname(__file__), path, outputName + ".csv")
	csvfile = open(outputfile, "w")
	fieldnames = generateFieldnames("output")
	print fieldnames
	print "len of data is: ", len(coalescedData)
	writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
	writer.writeheader()
	# print coalescedData[0]
	for i in range(len(coalescedData[0])):
		print 5
		
	# for i in range(len(coalescedData)):



def generateFileNames(filename):
	return [filename + str(i) + ".csv" for i in range(NUM_FILES)]


def main():
	filenames = generateFileNames("acoustic collimator actual size results")
	coalescedData, freqList = coalesce(filenames, "Paper Copy Actual Size")
	rewriteData(coalescedData, freqList, PATH, "output")

main()

	# def writeSingleOutput(self, outputfile, index):
	# 	outputPath = os.path.join(self.dir, self.pathToFolder + outputfile + str(index) + ".csv")
	# 	print outputPath
	# 	csvfile = open(outputPath, "w")
	# 	fieldnames = ["Frequency", "Real", "Imaginary"]
	# 	writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
	# 	writer.writeheader()
	# 	for freq in self.transmission[index]:
	# 		tempKey = self.transmission[index][freq].keys()[0] #only one key 
	# 		real, imag = self.getArgs(self.transmission[index][freq][tempKey])
	# 		writer.writerow({'Frequency': freq, 'Real': real, 'Imaginary': imag})