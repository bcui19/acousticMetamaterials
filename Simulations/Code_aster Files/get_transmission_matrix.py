import os 
import aster_processing as ap
import copy

#define constants
def stripEnd(line):
	line = line.strip("\n")
	return line


class transmissionMatrix(object):
	def __init__(self, filename):
		self.dir = os.path.dirname(__file__)
		self.args = self.loadFilenames(filename)
		self.getAster()

	#from the filename path, load all of the filenames that will need to be read into a list
	def loadFilenames(self, filename):
		filePath = os.path.join(self.dir, filename)
		with open(filePath) as f:
			lines = f.readlines()
			for i in range(len(lines)):
				lines[i] = stripEnd(lines[i])
		# print lines
		return lines

	def getAster(self):
		for filename in self.args:
			filePath = os.path.join(self.dir, filename)
			ap.main(filePath)



def main():
	tm = transmissionMatrix("filenames.txt")

main()