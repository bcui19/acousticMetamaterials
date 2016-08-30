#include <vector>
#include <map>
#include <math.h>

class sphericalVelocity {


public:

	//initializing spherical velocity
	sphericalVelocity();

	// destructor of spherical velocity
	virtual ~sphericalVelocity();

	//actually performs the calculations of the spherical velocity
	virtual void calculateSphericalVelocity();

	//returns the velocity at each port
	virtual <vector> returnSphericalVelocity();


private:
	double inputAmplitude;
	

}