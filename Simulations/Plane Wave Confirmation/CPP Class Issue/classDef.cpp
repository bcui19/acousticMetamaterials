#include <iostream>

using namespace std;

struct location {
	double xCoord;
	double yCoord;
};

class port{
public:
	port();
	~port();
	//define variables
	location Loc;
	int temp;

	//define methods
	void init(location loc);
	void printLoc();
	double returnX() const;
	double returnY() const;

};

port :: port() {
}

port :: ~port() {
}

//begin port class functions
void port :: init (location loc) {
	Loc = loc;
}

void port :: printLoc () {
	cout << "xcoord is: " << Loc.xCoord << endl;
	cout << "ycoord is: " << Loc.yCoord << endl;
}

double port :: returnX() const {
	return Loc.xCoord;
}

double port :: returnY() const {
	return Loc.yCoord;
}

// bool operator<(const port & a, const port & b) {
// 	return a.returnX() < b.returnX();
// }



//Begin detector class
class detector : public port {
public:
	detector();
	~detector();
// private:
	// bool operator<(const detector &b);
};

detector :: detector() {
}

detector :: ~detector() {
}

//binary operator
bool operator<(const detector & a, const detector & b){
	return a.returnX() < b.returnX();
}








