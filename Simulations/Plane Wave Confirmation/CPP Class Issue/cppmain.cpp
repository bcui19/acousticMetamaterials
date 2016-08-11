#include <iostream>
#include <map>
#include <vector>

#include "classDef.h" // This is the .h file that I'm importing

using namespace std;

static const int numIt = 10;
static const int numDetector = 12;

//uncomment this line and everything works 
// bool operator<(const detector & a, const detector &b) {
// 	return a.returnX() < b.returnX();
// }


//creates a map which has a key to a second map, whose key is a detector
//the issue is the imbedded map, it says there is no comparison operator
static void generateMap(map<int, map <detector, vector <int> > > &inputMap) {
	for (int i = 0; i < numIt; i ++) {

		map <detector, vector<int> > currMap;
		for (int j = 0; j < numDetector; j ++) {
			struct location tempLoc = {(double) j, (double) i};
			detector tempDetector;
			tempDetector.init(tempLoc);
			vector <int> currVector;
			for (int num = 0; num < numIt; num ++) {
				currVector.push_back(num);
			}
			currMap[tempDetector] = currVector;
		}
	}
}


int main () {
	map <int, map <detector, vector <int> > > inputMap;

	generateMap(inputMap);

	return 0;
}