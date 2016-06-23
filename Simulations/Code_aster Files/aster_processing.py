'''
Working on parsing out code aster files
'''


import os 


#just some random constants used for formatting from code_aster
FILE_OFFSET = 59
OFFSET_INDEX = 2 #how far from template2 to the key line  
KEY_INDEX = 7 #Where in the key line is the key located
TABLE_OFFSET_KEY = 2 #how many lines from the key line do I start
TABLE_OFFSET_TEMPLATE = 4 #how many lines from the key line do I start

template1 = ['', '======>']
template2 = ['', '------>']
blank_line = ['', '']
blank = ''

class code_aster(object):
	def __init__(self, filename, lineStart):
		dir = os.path.dirname(__file__)
		self.file = filename
		self.path = os.path.join(dir, filename)
		self.intxDict = {}
		self.presDict = {}
		self.loadData(lineStart)

	def getDicts(self):
		return self.intxDict, self.presDict

	#takes in a list which represents a line and removes the blanks
	#returns a map from the node to the corresponding values
	#assumes the line is either pressure or the other field character
	def remBlanks(self, line):
		key = line[1]
		tempList = []
		returnDict = {}
		for i in range(2,len(line)):
			if line[i] == blank:
				continue
			tempList.append(line[i])
		returnDict[key] = tempList
		return returnDict

	#removes the '\n' character from the end of the line list
	def stripEnd(self, line):
		line[len(line)-1] = line[len(line)-1].strip("\n")
		return line

	#finds the offset from the input 
	def findOffset(self, lines, startIndex):
		counter = 0
		line = []
		while cmp(line, template2) != 0:
			counter += 1
			line = self.stripEnd(lines[startIndex + counter].split(' '))
		return counter

	#assumes the startIndex includes the offset
	#internally adjusts the offset to reach the beginning of the table 
	def getKey(self, lines, startIndex):
		offset = self.findOffset(lines, startIndex) + OFFSET_INDEX
		line = self.stripEnd(lines[startIndex + offset].split(' '))
		key = line[KEY_INDEX]
		offset += TABLE_OFFSET_KEY
		return float(key), offset

	def createMapping(self, lines, startIndex, offset):
		tempList = []
		returnDict = {}
		while True:
			line = self.stripEnd(lines[startIndex + offset].split(' '))
			if cmp(line, blank_line) == 0:
				break
			tempDict = self.remBlanks(line) #Dictionary of node Number to corresponding Values
			tempList.append(tempDict)
			offset += 1
		return offset, tempList

	#Start index will be passed in as the index in lines to template1
	def parseData(self, lines, startIndex):
		counter = 0
		currKey, offset = self.getKey(lines, startIndex) #startIndex including offset
		#Gets information from the first table
		offset, tempList = self.createMapping(lines, startIndex, offset)
		self.intxDict[currKey] = tempList
		#gets the offset from the end of the first table to the arrow
		newOffset = self.findOffset(lines, startIndex + offset)
		newOffset += offset
		#from the first arrow go to the start of the table and start parsing data
		offset, tempList = self.createMapping(lines, startIndex, newOffset + TABLE_OFFSET_TEMPLATE)
		self.presDict[currKey] = tempList

	
	def loadData(self, lineStart):
		with open(self.path) as f:
			lines = f.readlines() #reads the lines 
			data = []
			for i in range(lineStart, len(lines)):
				line = lines[i].split(' ')
				line = self.stripEnd(line)

				#confirms that the line is template1 otherwise continues
				if not reduce(lambda v1, v2: v1 and v2, map(lambda v: v in line, template1)):
					continue
				self.parseData(lines, i)



#currently parses out code from the .resu file from code_aster and then puts the resultant data structures into
#two separate dictionaries where they are lists of dictionaries
#does this for a singular file
def main(filename):
	file = code_aster(filename, FILE_OFFSET)
	intxDict, presDict = file.getDicts()
	# print intxDict
	return intxDict, presDict
	# files = code_aster("test_output.resu", FILE_OFFSET)
	# intxDict, presDict = files.getDicts()
	# print intxDict
	# return intxDict, presDict

# main()

