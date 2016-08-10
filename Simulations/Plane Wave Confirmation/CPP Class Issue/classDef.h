struct location{
	double xCoord;
	double yCoord;
};


class port {
public:
	port();
	~port();

	location Loc;

	void init(location Loc);
	double returnX() const;
	double returnY() const;
// private:
	// bool operator<(const port & a, const port & b);

};

//inherits from the port class
class detector : public port {
public:
	detector();
	~detector();
	// bool operator<(const detector &b);
};