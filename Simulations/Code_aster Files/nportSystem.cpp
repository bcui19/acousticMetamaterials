/*
Program generates the Matrices and vectors needed to solve the linear 
system of equations:

a(w)x(w) = b(w)

Where a is a 8Nx8N matrix x represents the solution pressure and velocity conditions,
and b represents the system that we want to satisfy, and it will solve for the matrix x(w)
*/

//All of the #includes for linking
#include <iostream>
#include <fstream>
#include <vector>
#include <map>
#include <sstream>
#include <Eigen/Dense>
#include <math.h> 

using namespace Eigen;
using namespace std;

//Struct definition
struct connectionPair {
	int first;
	int second;
};


//Constants for coding
const string TRANSMISSION_VALUES = "Paper/Paper Copy independent/coalesced transmission values.csv";
const string TRANSMISSION_WEIGHTS = "Paper/Paper Copy independent/calculated transmission values.csv";
const string TRANSMISSION_PRIME = "Paper/Paper Copy independent/transmission prime values.csv";

const int NUM_CYCLES = 4; //Matrix dimensions
const int NUM_STRUCTURES = 2; //Defines the number of linked structures
const int MATRIX_DIM = pow(NUM_CYCLES,2); // Dimension of the final matrix
const int NUM_CLOSED = 4;
const int NUM_PORTS = 2;
vector <int> CLOSED_VECTOR, PORT_VECTOR;
vector<connectionPair> CONNECTION_VECTOR;


static void csvMapExtract(map<string, vector<double> > &transmissionMap, string inputFile);
static void printMap(map<string, vector<double> > currMap);
static void retreiveData(map<string, vector<double> > &transmissionMap, map<string, vector<double> > &transmissionVal, map<string, vector<double> > &transmissionPrime);
static void compileMatrix(map<string, vector<double> > currMap, map <string, MatrixX4cd> &compiledMatrix);
static void generateSingleMatrix(string key, map<string, vector <double > > currMap, MatrixXcd &finalMatrix);
static void systemSolve(map<string, vector <double> > currMap);
static void generateSolutionVector(VectorXcd &solutionVector);

//initialize Closed Vector
static void initClosedVect(){
	CLOSED_VECTOR.push_back(2);
	CLOSED_VECTOR.push_back(3);
	CLOSED_VECTOR.push_back(5);
	CLOSED_VECTOR.push_back(8);
}

//helper that takes two ports and puts them into the connection pair
static void initConnectionPair(connectionPair &currPair, int port1, int port2) {
	currPair.first = port1;
	currPair.second = port2;
}

//initialize Connection Vector
static void initConnectionVect() {
	connectionPair tempPort;
	initConnectionPair(tempPort, 4, 6);
	CONNECTION_VECTOR.push_back(tempPort);
}

//initializes port vector
static void initPortVect() {
	PORT_VECTOR.push_back(1);
	PORT_VECTOR.push_back(7);	
}

//Overall initialize vector function
static void initializeVectors() {
	initClosedVect();
	initConnectionVect();
	initPortVect();
}

//Helper function to get the velocity column to insert a value
//given an input value into the function
static int getVelocity_Col(int currVal){
	return ((currVal-1)/4) * 8 + NUM_CYCLES + (currVal -1) %4;
}

//Helper function to get the pressure column to insert a value given 
//an input value into the function
static int getPressure_Col(int currVal){
	return ((currVal-1)/4) * 8 + (currVal - 1)%4;
}


int main() {
	initializeVectors();
	map<string, vector<double> > transmissionMap; // Just the real and imaginary values of pressure
	map<string, vector<double> > transmissionVal; // The actual weights in the transmission matrix
	map<string, vector<double> > transmissionPrime; // The weights for tranmission prime
	retreiveData(transmissionMap, transmissionVal, transmissionPrime);

	systemSolve(transmissionVal);

	return 0;
}

static void systemSolve(map<string, vector <double> > currMap) {
	MatrixXcd finalMatrix = MatrixXcd::Zero(MATRIX_DIM, MATRIX_DIM);
	generateSingleMatrix("temp", currMap, finalMatrix);
	
	VectorXcd solutionVector = VectorXcd::Zero(MATRIX_DIM);
	generateSolutionVector(solutionVector);

	// cout << "Solution Vector is: " << solutionVector << endl << "Solution matrix is: " << finalMatrix << endl;
	VectorXcd resultMatrix = finalMatrix.colPivHouseholderQr().solve(solutionVector);
	cout << resultMatrix;
}

static void generateSolutionVector(VectorXcd &solutionVector) {
	solutionVector[MATRIX_DIM - 2] = 2e-13;
	solutionVector[MATRIX_DIM - 1] = 3e-13;
}


//generates the ports that are closed
//Takes in the closed port matrix and manipulates it to generate something nice
static void generateClosedPorts(MatrixXcd & closedMatrix) {
	for (int row = 0; row < CLOSED_VECTOR.size(); row ++) {
		int col = getVelocity_Col(CLOSED_VECTOR[row]);
		// cout << "col is : " << col << endl;
		closedMatrix(row, col) = 1; 
	}
	// cout << closedMatrix << endl << endl;
}

//Given a connectionPair struct, update the matrix so the given parameters are satisfied
static void updateConnectionMatrix(MatrixXcd & connectionMatrix, int row, connectionPair currPair) {
	int presCol = getPressure_Col(currPair.first);
	int presCol_next = getPressure_Col(currPair.second);
	connectionMatrix(row, presCol) = 1;
	connectionMatrix(row, presCol_next) = 1;
	
	int velCol = getVelocity_Col(currPair.first);
	int velCol_inverse = getVelocity_Col(currPair.second);
	connectionMatrix(row, velCol) = 1;
	connectionMatrix(row, velCol_inverse) = -1;
}

//Funciton used to generate the connection ports
static void generateConnectionPorts(MatrixXcd & connectionMatrix) {
	//iterate through the number of connection rows
	for (int row = 0; row < CONNECTION_VECTOR.size() * 2; row ++) {
		for (vector<connectionPair>::iterator itv = CONNECTION_VECTOR.begin(); itv != CONNECTION_VECTOR.end(); itv ++) {
			updateConnectionMatrix(connectionMatrix, row, *itv);
		}
	}
}

//Generate the matrix for the ports
static void generatePortMatrix(MatrixXcd & portMatrix) {
	for (int row = 0; row < PORT_VECTOR.size(); row ++) {
		int col = getPressure_Col(PORT_VECTOR[row]);
		portMatrix(row, col) = 1;
	}
}
//Generate the intial large transmission matrix
static void generate_TransmissionNode_Matrix(MatrixXcd &transmissionNode, string key, map<string, MatrixX4cd> compiledMatrix) {
	MatrixXcd tempMatrix = MatrixXcd::Zero(NUM_CYCLES * NUM_STRUCTURES, MATRIX_DIM);
	MatrixXcd identityMatrix = MatrixXcd::Identity(NUM_CYCLES, NUM_CYCLES);
	MatrixXcd zeroMatrix = MatrixXcd::Zero(NUM_CYCLES, NUM_CYCLES);

	transmissionNode << identityMatrix, -compiledMatrix[key], zeroMatrix, zeroMatrix, zeroMatrix, zeroMatrix, identityMatrix, -compiledMatrix[key];

}

//generate a singular solution matrix
static void generateSingleMatrix(string key, map<string, vector <double > > currMap, MatrixXcd &finalMatrix) {
	map <string, MatrixX4cd> compiledMatrix;
	compileMatrix(currMap, compiledMatrix);

	MatrixXcd transmissionNode = MatrixXcd::Zero(NUM_CYCLES * NUM_STRUCTURES, MATRIX_DIM);
	map<string, MatrixX4cd>:: iterator it = compiledMatrix.begin();

	generate_TransmissionNode_Matrix(transmissionNode, it->first, compiledMatrix);


	MatrixXcd closedMatrix = MatrixXcd::Zero(NUM_CLOSED, MATRIX_DIM);
	MatrixXcd connectionMatrix = MatrixXcd::Zero(MATRIX_DIM/2 - NUM_CLOSED - NUM_PORTS, MATRIX_DIM);
	MatrixXcd portMatrix = MatrixXcd::Zero(NUM_PORTS, MATRIX_DIM);
	generateClosedPorts(closedMatrix);
	generateConnectionPorts(connectionMatrix);
	generatePortMatrix(portMatrix);

	finalMatrix << transmissionNode, closedMatrix, connectionMatrix, portMatrix;

}

//Takes in a map of complex values, and then generates the associated matrices
static void compileMatrix(map<string, vector<double> > currMap, map <string, MatrixX4cd> &compiledMatrix) {
	for (map<string, vector<double> > :: iterator itm = currMap.begin(); itm != currMap.end(); itm ++) {
		vector <double> tempVect = currMap[itm->first]; // gets the vector associated with the current key

		MatrixX4cd tempMatrix = MatrixX4cd::Zero(4,4);
		int counter = 0;
		for (vector<double>:: iterator itv = tempVect.begin(); itv != tempVect.end(); itv += 2) {
			int row = counter/4;
			int col = counter%4;
			vector<double>:: iterator tempIt = next(itv, 1);
			complex <double> tempComp = complex<double>(*itv, *tempIt);
			tempMatrix(row, col) = complex<double> (*itv, *tempIt);
			counter ++;
		}
		compiledMatrix[itm->first] = tempMatrix;
	}

}

static void retreiveData(map<string, vector<double> > &transmissionMap,
	map<string, vector<double> > &transmissionVal, map<string, vector<double> > &transmissionPrime) {
	csvMapExtract(transmissionMap, TRANSMISSION_VALUES);
	csvMapExtract(transmissionVal, TRANSMISSION_WEIGHTS);
	csvMapExtract(transmissionPrime, TRANSMISSION_PRIME);
}
//for a given line, iterates over the line and extracts the line and adds it to the map with 
//the given key (frequency)
static void extractLine(const string line, map<string, vector<double > > &transmissionMap) {
	int counter = 0;
	string currVal;
	string key;
	vector<double> tempVect;
	stringstream ss(line);

	while(getline(ss, currVal, ',')) {
		if (counter == 0) {
			key = currVal;
			counter ++;
			continue;
		}
		tempVect.push_back(stod(currVal));
		counter ++;
	}
	transmissionMap[key] = tempVect;
}

//extracts the data from the CSV file
static void csvMapExtract(map<string, vector<double> > &transmissionMap, string inputFile) {
	ifstream csvFile(inputFile);
	string line;
	int lineNum = 0;
	while(getline(csvFile, line)) {
		if (lineNum == 0) {
			lineNum ++;
			continue;
		}
		extractLine(line, transmissionMap);
	}
}

//prints out the map, can hand check to make sure the map is stored properly
static void printMap(map<string, vector<double > > currMap) {
	for (map<string, vector<double> >:: iterator itm = currMap.begin(); itm != currMap.end(); itm ++) {
		cout << "key is: " << itm->first << " vals are: ";
		vector<double> currVector = currMap[itm->first];
		//each iteration covers a key which maps to a vector of floats 
		//this loop loops through the floats
		for (vector<double>:: iterator itv = currVector.begin(); itv != currVector.end(); itv ++) {
			cout << *itv << ", ";
		}
		cout << endl;
	}

}
