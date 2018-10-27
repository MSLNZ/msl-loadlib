// cpp_lib.cpp
// Examples that show how to pass various data types between Python and a C++ library.
//
// Compiled using:
//   g++ cpp_lib.cpp -fPIC -shared -Bstatic -Wall -o cpp_lib64.so
//
#include <math.h>
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

// this function is not exported to the shared library
double distance(Point p1, Point p2) {
    double d = sqrt(pow(p1.x - p2.x, 2) + pow(p1.y - p2.y, 2));
    return d;
}

double distance_4_points(FourPoints p) {
    double d = distance(p.points[0], p.points[3]);
    for (int i = 1; i < 4; i++) {
        d += distance(p.points[i], p.points[i-1]);
    }
    return d;
}

double distance_n_points(NPoints p) {
    if (p.n < 2) {
        return 0.0;
    }
    double d = distance(p.points[0], p.points[p.n-1]);
    for (int i = 1; i < p.n; i++) {
        d += distance(p.points[i], p.points[i-1]);
    }
    return d;
}
