struct location {
	double xCoord;
	double yCoord;
};

class port{
public:
	void init(location loc);
	void printLoc();
	double returnX() const;
	double returnY() const;
	bool operator<(const port & b);
	location Loc;

private:
	int temp;
// protected:

};


class detector : public port {
	bool operator<(const detector & b);


};

// class detector {
// public:
// 	void init(location loc);
// 	void printLoc();
// 	void returnX();
// 	void returnY();

// private:
// 	location Loc;


// };

