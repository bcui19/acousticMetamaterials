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
#include <iomanip> //used for set precision function 

using namespace Eigen;
using namespace std;

//Struct definition
struct connectionPair {
	int first;
	int second;
};


//Constants for coding
const string TRANSMISSION_VALUES = "Paper/rightFreq identity/coalesced transmission values.csv";
const string TRANSMISSION_WEIGHTS = "Paper/rightFreq identity/calculated transmission values.csv";
const string TRANSMISSION_PRIME = "Paper/rightFreq identity/transmission prime values.csv";
const string OUTPUTFILE = "Paper/rightFreq identity/new code calculated two cells v";

const int NUM_CYCLES = 4; //Input transmission Matrix dimensions
const int NUM_STRUCTURES = 2; //Defines the number of linked structures
// const int MATRIX_DIM = 8;
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
static void systemSolve(map<string, vector <double> > currMap, map<string, VectorXcd> &resultMap, int iterationNum);
static void generateSolutionVector(VectorXcd &solutionVector, int iterationNum);
static void outputCSV(map<string, VectorXcd> resultMap, string outputFile);
static string makeFilename(int iterationNum);
static void runSolver(map<string, vector <double> > transmissionWeights);


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

	// printMap(transmissionVal);

	runSolver(transmissionVal);

	return 0;
}

static void runSolver(map<string, vector <double> > transmissionWeights) {
	for (int i = 0; i < NUM_PORTS; i ++) {
		map<string, VectorXcd> resultMap;
		systemSolve(transmissionWeights, resultMap, i);
		outputCSV(resultMap, makeFilename(i));
	}
}

static void systemSolve(map<string, vector <double> > currMap, map<string, VectorXcd> &resultMap, int iterationNum) {
	cout << "in system solve" << endl;
	MatrixXcd tempFinal;
	VectorXcd tempresu;
	VectorXcd tempSol;
	for (map<string, vector<double> >:: iterator itm = currMap.begin(); itm != next(currMap.begin(), 1); itm ++) {
		// cout << "frequency is: " << itm->first << endl;
		MatrixXcd finalMatrix = MatrixXcd::Zero(MATRIX_DIM, MATRIX_DIM);
		generateSingleMatrix(itm->first, currMap, finalMatrix); // pass in the current key to the map
	

		VectorXcd solutionVector = VectorXcd::Zero(MATRIX_DIM);
		generateSolutionVector(solutionVector, iterationNum);

		// cout << "Solution Vector is: " << solutionVector << endl << "Solution matrix is: " << finalMatrix << endl;
		VectorXcd resultVector = finalMatrix.colPivHouseholderQr().solve(solutionVector);

		// cout << resultVector << endl << endl;
		// cout << "solutionVector is: " << solutionVector << endl << endl << endl;
		// cout << "solving matrix is: " << finalMatrix << endl << endl << endl;
		resultMap[itm->first] = resultVector;
		tempFinal = finalMatrix;
		tempresu = solutionVector;
		tempSol = resultVector;
	}

	cout << tempFinal << endl;
	cout << tempresu << endl;
	cout << tempSol << endl;

}

//updates a zero'd out solution vector (right hand side) to get a proper solution vector
//currently only updates a singular entry 
static void generateSolutionVector(VectorXcd &solutionVector, int iterationNum) {
	solutionVector[MATRIX_DIM - 1] = complex <double> (1.0, 5.0);
	solutionVector[MATRIX_DIM - NUM_PORTS + iterationNum] = 1;
	// solutionVector[MATRIX_DIM - 2] = 1;
	// solutionVector[MATRIX_DIM-1] = 1;
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
static void updateConnectionMatrix(MatrixXcd & connectionMatrix, int row, connectionPair currPair, int connectionCounter) {
	int presCol = getPressure_Col(currPair.first);
	int presCol_next = getPressure_Col(currPair.second);
	connectionMatrix(2*row, presCol) = 1;
	connectionMatrix(2*row, presCol_next) = -1;
	
	int velCol = getVelocity_Col(currPair.first);
	int velCol_inverse = getVelocity_Col(currPair.second);
	connectionMatrix(2*row + 1, velCol) = 1;
	connectionMatrix(2*row + 1, velCol_inverse) = 1;
	// cout << connectionCounter << endl;

}

//Funciton used to generate the connection ports
static void generateConnectionPorts(MatrixXcd & connectionMatrix) {
	//iterate through the number of connection rows
	for (int row = 0; row < CONNECTION_VECTOR.size(); row ++) {
		for (vector<connectionPair>::iterator itv = CONNECTION_VECTOR.begin(); itv != CONNECTION_VECTOR.end(); itv ++) {
			updateConnectionMatrix(connectionMatrix, row, *itv, row);
		}
	}
}

//Generate the matrix for the ports
static void generatePortMatrix(MatrixXcd & portMatrix) {
	for (int row = 0; row < PORT_VECTOR.size(); row ++) {
		int col = getVelocity_Col(PORT_VECTOR[row]);
		portMatrix(row, col) = 1;
	}
}

//Fills the first block "identity plus tranmission weights matrix"
static void fillBlock(MatrixXcd &transmissionNode, int blockNum, MatrixX4cd currTransmission) {
	for (int rowIter = 0; rowIter < NUM_CYCLES; rowIter ++) {
		for (int colIter = 0; colIter < NUM_CYCLES * 2; colIter ++) {
			int currRow = blockNum * NUM_CYCLES + rowIter;
			int currCol = blockNum * (NUM_CYCLES * 2) + colIter;
			
			if (rowIter == colIter)
				transmissionNode(currRow, currCol) = 1;
			if (colIter > 3)
				transmissionNode(currRow, currCol) = -currTransmission(rowIter, colIter-NUM_CYCLES);
		}
	}
}

//Generate the intial large transmission matrix
static void generate_TransmissionNode_Matrix(MatrixXcd &transmissionNode, string key, map<string, MatrixX4cd> compiledMatrix) {
	MatrixXcd tempMatrix = MatrixXcd::Zero(NUM_CYCLES * NUM_STRUCTURES, MATRIX_DIM);
	MatrixXcd identityMatrix = MatrixXcd::Identity(NUM_CYCLES, NUM_CYCLES);
	MatrixXcd zeroMatrix = MatrixXcd::Zero(NUM_CYCLES, NUM_CYCLES);

	//iterates through all of the structures
	for (int i = 0; i < NUM_STRUCTURES; i ++) {
		fillBlock(transmissionNode, i, compiledMatrix[key]);
	}
}

//generate a singular solution matrix 
//the A p(w) = b(w) in the equation 
static void generateSingleMatrix(string key, map<string, vector <double > > currMap, MatrixXcd &finalMatrix) {
	map <string, MatrixX4cd> compiledMatrix;
	compileMatrix(currMap, compiledMatrix);

	MatrixXcd transmissionNode = MatrixXcd::Zero(NUM_CYCLES * NUM_STRUCTURES, MATRIX_DIM);

	generate_TransmissionNode_Matrix(transmissionNode, key, compiledMatrix);


	MatrixXcd closedMatrix = MatrixXcd::Zero(NUM_CLOSED, MATRIX_DIM);
	MatrixXcd connectionMatrix = MatrixXcd::Zero(MATRIX_DIM/2 - NUM_CLOSED - NUM_PORTS, MATRIX_DIM);
	MatrixXcd portMatrix = MatrixXcd::Zero(NUM_PORTS, MATRIX_DIM);
	generateClosedPorts(closedMatrix);
	generateConnectionPorts(connectionMatrix);
	generatePortMatrix(portMatrix);

	finalMatrix << transmissionNode, closedMatrix, connectionMatrix, portMatrix;

}

//Takes in a map of complex values, and then rearranges the data for the associated matrices
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

static string generateCSVString(VectorXcd currVector) {
	string outputString = "";
	// cout << "current size is: " << currVector.size()  << endl;
	// cout << currVector << endl;
	for (int i = 0; i < currVector.size(); i ++) {

		stringstream tempStream;
		tempStream << fixed << setprecision(45) << currVector[i].real() << ",";
		tempStream << fixed << setprecision(45) << currVector[i].imag() << ",";

		outputString += tempStream.str();
	}
	outputString += "\n";

	return outputString;
}

//Makes the filename to be used for the outputCSV
static string makeFilename(int iterationNum) {
	string tempFilename = OUTPUTFILE;
	for (int i = 0; i < NUM_PORTS; i ++) {
		if (i == iterationNum)
			tempFilename += "1-1, ";
		else
			tempFilename += "0, ";
	}
	return tempFilename + ".csv";
}

static string generateCSVHeader() {
	string header = "Frequency,";
	for (int i = 0; i < NUM_STRUCTURES * 2; i ++) {
		for (int j = 0; j < NUM_CYCLES; j ++) {
			header += i%2 == 0 ? "pressure ": "velocity ";
			header += to_string(i/2*NUM_CYCLES + j) + " real,";
			header += i%2 == 0 ? "pressure ": "velocity ";
			header += to_string(i/2*NUM_CYCLES + j) + " imag,";
		}
	}
	cout << header << endl;
	return header + "\n";
}

static void outputCSV(map<string, VectorXcd> resultMap, string outputfile) {
	ofstream output;
	output.open(outputfile);
	//iterating through all of the result map
	output << generateCSVHeader();
	for (map<string, VectorXcd>:: iterator itm = resultMap.begin(); itm != resultMap.end(); itm ++) {
		output << itm->first + ",";
		output << generateCSVString(resultMap[itm->first]);
	}
	output.close();

}

//takes in the data that we want and stores it into maps
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
		cout << endl << endl << endl;
	}

}
