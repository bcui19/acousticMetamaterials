/*
//
//
*/

#include <iostream>
#include <vector>
#include <map>
#include <Eigen/Dense>
#include <math.h>
#include <cmath>
#include "planeWaveClass.h"
#include <typeinfo>

using namespace std;
// using namespace planeWaveClass;

//define variable numbers
const int NUM_PORTS = 11;
const int NUM_DETECTORS = 100;
const int DETECTOR_MID = 0;
const int NUM_ROWS = 10;


//Define spacing constants
const double PORT_SPACING = 0.0011375;
const double DETECTOR_SPACING = 0.00025;
const double ROW_SPACING = 0.05;
const double DETECTOR_OFFSET = 1.0;

const int MIDPOINT = (NUM_PORTS-1)/2.0 * PORT_SPACING;

//define frequency constants
const int FREQ_LOW = 25000;
const int FREQ_HIGH = 25012;
const int FREQ_DIFF = 12;
const int SPEED_OF_SOUND = 343;

struct detectDist {
	detector currDetect;
	double dist;
};

struct detectConst {
	detector currDetect;
	double constVal;
};

bool operator<(const detector & x, const detector & y) {
		return x.returnX() < y.returnX();
}

//define global constants
map <int, vector<detector> > detectorList;
vector<port> portList;

//define function prototypes
static void printDetectors();
static void printPorts();
static void runCalculation();
static void createDistanceDict(map<int, map < detector, vector <detectDist> > > &distanceDict, map<int, map <detector, vector <detectConst> > > &constDict, int freq);


int main() {
	runCalculation();
	// cout << "linking works" << endl;
	// cout << complex <int> (1,0) << endl;
	// struct location tempLoc = {5, 4};
	// cout << tempLoc.xCoord << endl;
	// planeWave temp = planeWave(tempLoc);
	// port temp;
	// temp.init(tempLoc);
	return 0;
}

static void generateDetectors(){
	for (int i = 0; i < NUM_ROWS; i ++) {
		vector <detector> currVec;
		for (int j = 0; j < NUM_DETECTORS; j++) {
			struct location currLoc = {((double) j) * DETECTOR_SPACING, DETECTOR_OFFSET + ((double) i) * ROW_SPACING};
			detector tempDetector;
			tempDetector.init(currLoc);
			currVec.push_back(tempDetector);
		}
		detectorList[i] = currVec;
	}
	// printDetectors();
}

static void printDetectors() {
	for (map<int, vector<detector> > :: iterator itm = detectorList.begin(); itm != detectorList.end(); itm ++) {

		vector<detector> currVector = detectorList[itm->first];
		for (vector<detector> :: iterator itv = currVector.begin(); itv != currVector.end(); itv++) {
			(*itv).printLoc();
		}
	}
}

static void generatePorts() {
	for (int i = 0; i < NUM_PORTS; i ++) {
		struct location currLoc = {(double) i * PORT_SPACING, 0};
		port tempPort;
		tempPort.init(currLoc);
		portList.push_back(tempPort);
	}
	// printPorts();
}

static void printPorts(){
	for (vector <port> :: iterator itv = portList.begin(); itv != portList.end(); itv++) {
		(*itv).printLoc();
	}
}

static void runCalculation() {
	generateDetectors();
	generatePorts();

	map <int, map <detector, vector<detectDist> > > distanceDict;
	map < int, map <detector , vector <detectConst> > > constDict;
	for (int freq = FREQ_LOW; freq < FREQ_HIGH; freq += 12) {
		createDistanceDict(distanceDict, constDict, freq);
	}
}

static double getWavelength(int freq) {
	return (double) SPEED_OF_SOUND/(double) freq;
}

static double calcWavenumber(int freq) {
	return 2.0*M_PI*getWavelength(freq);
}

static double calcConst(double distance, int freq) {
	return exp(calcWavenumber(freq) * distance)/distance;
}

static double calculateDist(detector currDetector, port currPort) {
	return pow((pow(currDetector.returnX() - currPort.returnX(), 2) + pow (currDetector.returnY()-currPort.returnY(), 2)), 0.5);
}

static void createDistanceDict(map<int, map < detector, vector <detectDist> > > &distanceDict, map<int, map <detector, vector <detectConst> > > &constDict, int freq) {
	for (map<int, vector<detector> > :: iterator itm = detectorList.begin(); itm != detectorList.end(); itm ++) {
		vector <detector> currVector = itm->second;
		map <detector, vector < detectDist> > distMap;
		map <detector, vector <detectConst> > constMap;

		for (vector <detector> :: iterator detectIt = currVector.begin(); detectIt != currVector.end(); detectIt ++) {
			vector <detectDist> distVector;
			vector <detectConst> constVector;

			for (vector <port> :: iterator portIt = portList.begin(); portIt != portList.end(); portIt ++) {


				double currDist = calculateDist(*detectIt, *portIt);
				double currConst = calcConst(currDist, freq);
				// cout << "currConst is: " << currConst << endl;
				struct detectDist currDistStruct = {(*detectIt), currDist};
				struct detectConst currConstStruct = {(*detectIt), currConst};
				
				distVector.push_back(currDistStruct);
				constVector.push_back(currConstStruct);

				// struct detectDist currDist = {(*detectIt), calculateDist(*detectIt, *portIt)};
				// cout << currDist.currDetect.returnY()<< endl;
			}
			distMap[*detectIt] = distVector;
			constMap[*detectIt] = constVector;
			// cout << distVector.size() << endl;
		}
		distanceDict[itm->first] = distMap;
		constDict[itm->first] = constMap;

	}

	//checking code can be ignored
	// for (map <int, vector <detectDist> > :: iterator itm = distanceDict.begin(); itm != distanceDict.end(); itm ++) {
	// 	cout << itm->first << endl;
	// }
}

static void createDifferences(map <int, map <detector, vector <detectConst> > > constDict, map <int, map <detector, vector <detectConst> > > & diffDict) {
	for (map <int, map < detector, vector < detectConst> > > :: iterator itm = constDict.begin(); itm != constDict.end(); itm ++) {
		cout << itm->first << endl;
	}
}

// static void createConstdict(map <int, vector <detectConst> > &constDict, map <int , vector <detectDist> > distanceDict) {
// 	for (map < int, vector <detector> > :: iterator itm = distanceDict.begin(); itm != distanceDict.end(); itm ++) {
// 		vector <detectDist> currVector = itm->second; //Current vector we need to iterate through

// 		vector <detectConst> constVector;
// 		for (vector <detectDict> :: iterator itv = currVector.begin(); itv != currVector.end(); itv++) {

// 		}

// 	}
// }



















