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

//Begin detector class
class detector : public port {
public:
	detector();
	~detector();

};



// //Begin detector class
// class detector {
// //define variables
// location Loc;

// //define methods
// void init(location loc);
// void printLoc();


// };

// void detector :: init(location loc) {
// 	Loc = loc;
// }

// void detector :: printLoc() {
// 	cout << "xcoord is: " << Loc.xCoord << endl;
// 	cout << "ycoord is: " << Loc.yCoord << endl;
// }
