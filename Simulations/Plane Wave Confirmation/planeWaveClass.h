struct location {
	int xCoord;
	int yCoord;
};

class port{
public:
	void init(location loc);
private:
	location Loc;
	int temp;
	void printLoc();

};


class detector {
public:
	void init(location loc);
private:
	location Loc;


};

