#include <cctype>
#include <iostream>
#include "cppLink.h"

using namespace std;


test::test(int temp){
    temporary = temp;
}

test::~test(){
}

void test::testFunction() {
    cout << "Test function works!" << endl;
    cout << std::to_string(temporary) << " is great" << endl;
}
