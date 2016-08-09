#include <iostream>

using namespace std;

struct location {
	int xCoord;
	int yCoord;
};

class port{

//define variables
location Loc;
int temp;

//define methods
void init(location loc);
void printLoc();

};

//begin port class
void port :: init (location loc) {
	Loc = loc;

}

void port :: printLoc () {
	cout << "xcoord is: " << Loc.xCoord << endl;
	cout << "ycoord is: " << Loc.yCoord << endl;
}


//Begin detector class
class detector {
//define variables
location Loc;

//define methods
void init(location loc);
void printLoc();


};

void detector :: init(location loc) {
	Loc = loc;
}

void detector :: printLoc() {
	cout << "xcoord is: " << Loc.xCoord << endl;
	cout << "ycoord is: " << Loc.yCoord << endl;
}
