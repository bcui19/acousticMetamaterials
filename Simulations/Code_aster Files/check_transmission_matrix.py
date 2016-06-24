#define Constants
# CEIL_DIFF = 0.000001
CEIL_DIFF = [1, 10e-5, 10e-10, 10e-15, 10e-20]
# CEIL_DIFF_LARGE = 1
# CEIL_DIFF_MED = 10e-5
# CEIL_DIFF_SMALL = 10e-17

def arrIndex(curVal):
	return 0 if curVal > 100 else 1 if curVal > 10e-3 else 2 if curVal > 10e-8 else 3 if curVal > 10e-12 else 4

#checks if d1 and d2 each have the same keys 
def checkKeys(d1, d2):
	k1 = d1.keys()
	k1.sort()
	k2 = d2.keys()
	k2.sort()
	return cmp(k1,k2)

#for a given 
def checkFrequency(n1, n2):
	keys = n1.keys()
	for i in range(len(keys)):
		curVal = n1[keys[i]]
		compareVal = n2[keys[i]]
		# print "curVal is: ", curVal
		if abs(curVal - compareVal) > CEIL_DIFF[arrIndex(abs(curVal))]:
			print "curVal is: ", curVal
			print "abs dif: ", abs(curVal - compareVal)
			return -1
	return 0

def checkValues(d1, d2):
	keys = d1.keys() #since we already know they have the same keys

	#each key is a frequency that maps to a dictionary of nodes
	for i in range(len(keys)):
		currVal = d1[keys[i]]
		compareVal = d2[keys[i]]
		if checkFrequency(currVal, compareVal) != 0:
			return -1

	return 0

#takes in two dictionaries and compares them
def compareDictionary(d1, d2):
	if checkKeys(d1, d2) != 0:
		return -1
	if checkValues(d1, d2) != 0:
		return -1
	return 0

#Used to check the similarity to make sure any linear combination works 
def main(tm1, tm2):
	for i in range(len(tm1)):#range(len(tm1)):
		print "same" if compareDictionary(tm1[i], tm2[i]) == 0 else "different"