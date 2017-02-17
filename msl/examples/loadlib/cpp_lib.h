// cpp_lib.h
// Contains the declaration of exported functions.
//

#define EXPORT __declspec(dllexport)   

extern "C" {

    // a + b
    EXPORT int add(int a, int b);

    // a - b
    EXPORT float subtract(float a, float b);

    // IF do_addition IS TRUE THEN a + b ELSE a - b
    EXPORT double add_or_subtract(double a, double b, bool do_addition);

    // multiply each element in 'x' by 'a'
    EXPORT void scalar_multiply(double a, double* xin, int n, double* xout);

    // reverse a string
    EXPORT void reverse_string_v1(const char* original, int n, char* reversed);

    // reverse a string and return it
    EXPORT char* reverse_string_v2(char* original, int n);

}