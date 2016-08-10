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
#include <complex>

using namespace std;
using namespace Eigen;
// using namespace planeWaveClass;

//define variable numbers
const int NUM_PORTS = 11;
const int NUM_DETECTORS = 100;
const int DETECTOR_MID = 0;
const int NUM_ROWS = 100;


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
	complex<double> constVal;
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
static void createDifferences(map <int, map <detector, vector <detectConst> > > constDict, map <int, map <detector, vector <detectConst> > > & diffDict);
static void generateKeys(const map <detector, vector <detectConst > > &currMap, vector<detector> & keys);

//Matrix function prototypes
static MatrixXcd generateMatrix(map <int, map <detector, vector<detectConst> > > diffDict);
static VectorXcd generateRHS(MatrixXcd & matrix);
static MatrixXcd reduceMatrix(MatrixXcd &matrix);
static VectorXcd leastSquaresSolve(MatrixXcd diffMatrix, VectorXcd rhs);
static VectorXcd renormalizeResult(VectorXcd vector);


//extra matrix helper functions
void removeRow(MatrixXcd& matrix, unsigned int rowToRemove);
static MatrixXcd removeColumn(MatrixXcd matrix, unsigned int colToRemove);


int main() {
	runCalculation();
	for (int i = 0; i < NUM_DETECTORS; i ++) {
		cout << i << endl;
	}
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
			struct location currLoc = {(double)(j - NUM_DETECTORS/2) * DETECTOR_SPACING, DETECTOR_OFFSET + ((double) i) * ROW_SPACING};
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
	map <int, map <detector, vector <detectConst> > > diffDict;

	int samplingPoint = 25;

	for (int freq = FREQ_LOW; freq < FREQ_HIGH; freq += 12) {
		createDistanceDict(distanceDict, constDict, freq);
		createDifferences(constDict, diffDict);
		MatrixXcd diffMatrix = generateMatrix(diffDict);
		VectorXcd rhs = generateRHS(diffMatrix);
		MatrixXcd reducedMatrix = reduceMatrix(diffMatrix);
		VectorXcd solution = leastSquaresSolve(reducedMatrix, rhs);
		VectorXcd normalized = renormalizeResult(solution);
		cout << "Matrix dimensions are: " << diffMatrix.cols() << " Cols and " << diffMatrix.rows() << " rows" << endl;
		cout << "vector dimensions are: " << normalized.rows() << " Rows and " << normalized.cols() << endl;
		VectorXcd pressureVec = diffMatrix * normalized;

		for (int i = 0; i < NUM_DETECTORS; i ++) {
			// cout << pressureVec(samplingPoint * NUM_DETECTORS + i) << endl;
		}

	}
}

static double getWavelength(int freq) {
	// cout << "wavelength is: " << (double) SPEED_OF_SOUND/(double) freq;
	return (double) SPEED_OF_SOUND/((double) freq);
}

static double calcWavenumber(int freq) {
	return 2.0*M_PI/getWavelength(freq);
}

static complex<double> calcConst(double distance, int freq) {
	complex<double> result =  exp(complex<double>(0.0, -1.0) * calcWavenumber(freq) * distance)/distance;
	// cout << result << endl;
	return result;
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
				complex<double> currConst = calcConst(currDist, freq);

				struct detectDist currDistStruct = {(*detectIt), currDist};
				struct detectConst currConstStruct = {(*detectIt), currConst};
				
				distVector.push_back(currDistStruct);
				constVector.push_back(currConstStruct);
			}
			distMap[*detectIt] = distVector;
			constMap[*detectIt] = constVector;
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
	for (map <int, map <detector, vector < detectConst> > > :: iterator itm = constDict.begin(); itm != constDict.end(); itm ++) {
		map <detector, vector <detectConst> > currMap = itm->second;

		vector <detector> currKeys;


		generateKeys(currMap, currKeys);

		detector refDetector = currKeys[NUM_DETECTORS/2];
		vector <detectConst> refVector = currMap[refDetector];

		map <detector, vector <detectConst> > tempResuMap;

		for (map <detector, vector <detectConst> > :: iterator detectIt = currMap.begin(); detectIt != currMap.end(); detectIt ++) {
			detector currDetector = detectIt->first;
			vector <detectConst> currVect = detectIt->second;

			vector <detectConst> resuVect;
			for (int i = 0; i < currVect.size(); i ++) {
				complex <double> tempResu = currVect[i].constVal - refVector[i].constVal;
				struct detectConst currConstStruct = {detectIt->first, tempResu};
				// cout << tempResu << endl;
				resuVect.push_back(currConstStruct);

			}
			tempResuMap[currDetector] = resuVect;
		}
		diffDict[itm->first] = tempResuMap;
	}
}

//generates the keys of a map 
//not generalized because I don't like to generalize functions in c++
static void generateKeys(const map <detector, vector <detectConst > > &currMap, vector<detector> & keys) {
	for (map <detector, vector <detectConst > > :: const_iterator itm = currMap.begin(); itm != currMap.end(); itm ++) {
		keys.push_back(itm->first);
	}
}

static MatrixXcd generateMatrix(map <int, map <detector, vector <detectConst> > >  diffDict){
	MatrixXcd resuMatrix(NUM_DETECTORS*NUM_ROWS, NUM_PORTS);
	int counter = 0;
	for (map<int, map<detector, vector<detectConst> > > :: iterator it = diffDict.begin(); it != diffDict.end(); it++) {
		map<detector, vector<detectConst> > currMap = it->second;

		for (map<detector, vector <detectConst> >:: iterator itm = currMap.begin(); itm != currMap.end(); itm ++) {

			vector<detectConst> currVector = itm->second;
			for (int i = 0 ; i < NUM_PORTS; i ++) {
				resuMatrix(counter, i) = currVector[i].constVal;
			}
			counter += 1;
		}
	}

	return resuMatrix;
}

//generates the right hand side of the matrix
static VectorXcd generateRHS(MatrixXcd & matrix) {
	VectorXcd returnVector;
	returnVector = -matrix.block(0, NUM_PORTS/2, NUM_DETECTORS*NUM_ROWS, 1);
	// cout << returnVector << endl;
	return returnVector;
}

static MatrixXcd reduceMatrix(MatrixXcd &matrix) {
	// cout << "cols before: " << matrix.cols() << "rows before: " << matrix.rows() << endl;
	return removeColumn(matrix, NUM_PORTS/2);
}

static VectorXcd leastSquaresSolve(MatrixXcd diffMatrix, VectorXcd rhs) {
	return diffMatrix.jacobiSvd(ComputeThinU |ComputeThinV).solve(rhs);
}

static MatrixXcd removeColumn(MatrixXcd matrix, unsigned int colToRemove) {
    unsigned int numRows = matrix.rows();
    unsigned int numCols = matrix.cols()-1;
    MatrixXcd matrixCopy = matrix;

    if( colToRemove < numCols )
        matrixCopy.block(0,colToRemove,numRows,numCols-colToRemove) = matrixCopy.block(0,colToRemove+1,numRows,numCols-colToRemove);

    matrixCopy.conservativeResize(numRows,numCols);
    return matrixCopy;
}

static VectorXcd renormalizeResult(VectorXcd vector) {
	VectorXcd result = VectorXcd::Zero(vector.rows()+1);
	// cout << vector.rows() << endl;
	for (int i = 0; i < result.rows(); i++) {
		if (i < NUM_PORTS/2)
			result(i) = vector(i);
		else if (i == NUM_PORTS/2)
			result(i) = complex<double> (1,0);
		else
			result(i) = vector(i-1);
	}
	// cout << result << endl;
	return result;
}

void removeRow(MatrixXcd & matrix, unsigned int rowToRemove) {
    unsigned int numRows = matrix.rows()-1;
    unsigned int numCols = matrix.cols();

    if( rowToRemove < numRows )
        matrix.block(rowToRemove,0,numRows-rowToRemove,numCols) = matrix.block(rowToRemove+1,0,numRows-rowToRemove,numCols);

    matrix.conservativeResize(numRows,numCols);
}


















