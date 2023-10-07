! fortran_lib.f90
!
! Basic examples of passing different data types to a FORTRAN function and subroutine.
!
! Compiled in Windows using:
! gfortran -fno-underscoring -fPIC fortran_lib.f90 -static -shared -o fortran_lib64.dll
!
	
! return the sum of two 8-bit signed integers
function sum_8bit(a, b) result(value)
    !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'sum_8bit' :: sum_8bit
    implicit none
    integer(1) :: a, b, value
    value = a + b
end function sum_8bit


! return the sum of two 16-bit signed integers
function sum_16bit(a, b) result(value)
    !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'sum_16bit' :: sum_16bit
    implicit none
    integer(2) :: a, b, value
    value = a + b
end function sum_16bit


! return the sum of two 32-bit signed integers
function sum_32bit(a, b) result(value)
    !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'sum_32bit' :: sum_32bit
    implicit none
    integer(4) :: a, b, value
    value = a + b
end function sum_32bit


! return the sum of two 64-bit signed integers
function sum_64bit(a, b) result(value)
    !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'sum_64bit' :: sum_64bit
    implicit none
    integer(8) :: a, b, value
    value = a + b
end function sum_64bit


! return the product of two 32-bit floating point numbers
function multiply_float32(a, b) result(value)
    !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'multiply_float32' :: multiply_float32
    implicit none
    real(4) :: a, b, value
    value = a * b
end function multiply_float32
    

! return the product of two 64-bit floating point numbers
function multiply_float64(a, b) result(value)
    !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'multiply_float64' :: multiply_float64
    implicit none
    real(8) :: a, b, value
    value = a * b
end function multiply_float64


! return True if 'a' > 0 else False 
function is_positive(a) result(value)
    !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'is_positive' :: is_positive
    implicit none
    logical :: value
    real(8) :: a
    value = a > 0.d0
end function is_positive

    
! if do_addition is True return a+b otherwise return a-b
function add_or_subtract(a, b, do_addition) result(value)
    !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'add_or_subtract' :: add_or_subtract
    implicit none
    logical :: do_addition
    integer(4) :: a, b, value
    if (do_addition) then
        value = a + b
    else
        value = a - b
    endif
end function add_or_subtract

    
! compute the n'th factorial of a 8-bit signed integer, return a double-precision number
function factorial(n) result(value)
    !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'factorial' :: factorial
    implicit none
    integer(1) :: n
    integer(4) :: i
    double precision value
    if (n < 0) then
        value = 0.d0
        print *, "Cannot compute the factorial of a negative number", n
    else
        value = 1.d0
        do i = 2, n
            value = value * i
        enddo
    endif
end function factorial


! calculate the standard deviation of an array.
function standard_deviation(a, n) result(var)
    !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'standard_deviation' :: standard_deviation
    integer :: n ! the length of the array
    double precision :: var, a(n)
    var = SUM(a)/SIZE(a) ! SUM is a built-in fortran function
    var = SQRT(SUM((a-var)**2)/(SIZE(a)-1.0))
end function standard_deviation


! compute the Bessel function of the first kind of order 0 of x
function besselj0(x) result(val)
    !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'besselj0' :: besselj0
    double precision :: x, val
    val = BESSEL_J0(x)
end function besselJ0


! reverse a string, 'n' is the length of the original string
subroutine reverse_string(original, n, reversed)
    !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'reverse_string' :: reverse_string
    !DEC$ ATTRIBUTES REFERENCE :: original, reversed
    implicit none
    integer :: i, n
    character(len=n) :: original, reversed
    do i = 1, n
        reversed(i:i) = original(n-i+1:n-i+1)
    end do
end subroutine reverse_string


! element-wise addition of two 1D double-precision arrays
subroutine add_1d_arrays(a, in1, in2, n)
    !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'add_1d_arrays' :: add_1d_arrays
    implicit none
    integer(4) :: n ! the length of the input arrays
    double precision :: in1(n), in2(n) ! the arrays to add (element-wise)
    double precision :: a(n) ! the array that will contain the element-wise sum
    a(:) = in1(:) + in2(:)
    end subroutine add_1d_arrays


! multiply two 2D, double-precision arrays. 
! NOTE: multi-dimensional arrays are column-major order in FORTRAN, 
!       whereas C (Python) is row-major order.
subroutine matrix_multiply(a, a1, r1, c1, a2, r2, c2)
    !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'matrix_multiply' :: matrix_multiply
    implicit none
    integer(4) :: r1, c1, r2, c2 ! the dimensions of the input arrays
    double precision :: a1(r1,c1), a2(r2,c2) ! the arrays to multiply
    double precision :: a(r1,c2) ! resultant array
    a = MATMUL(a1, a2)
end subroutine matrix_multiply
    