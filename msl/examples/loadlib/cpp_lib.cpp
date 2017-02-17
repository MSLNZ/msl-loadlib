// cpp_lib.cpp
// Examples that show how to pass various data types between Python and a C++ library.
//

#include "cpp_lib.h"

int add(int a, int b) {
    return a + b;
}

float subtract(float a, float b) {
    return a - b;
}

double add_or_subtract(double a, double b, bool do_addition) {
    if (do_addition) {
        return a + b;
    } else {
        return a - b;
    }
}

void scalar_multiply(double a, double* xin, int n, double* xout) {
    for (int i = 0; i < n; i++) {
        xout[i] = a * xin[i];
    }
}

void reverse_string_v1(const char* original, int n, char* reversed) {
    for (int i = 0; i < n; i++) {
        reversed[i] = original[n-i-1];
    }
}

char* reverse_string_v2(char* original, int n) {
    char* reversed = new char[n];
    for (int i = 0; i < n; i++) {
        reversed[i] = original[n - i - 1];
    }
    return reversed;
}
