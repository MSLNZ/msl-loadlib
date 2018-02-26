package nz.msl.examples;

import java.util.Random;


public class Matrix {

  /** The matrix, M */
  private double[][] m;
  
  /** Lower-triangular matrix representation, M=LU, in LU Decomposition */
  private Matrix L;

  /** Upper-triangular matrix representation, M=LU, in LU Decomposition */
  private Matrix U;

  /** A NxM orthogonal matrix representation, M=QR, in QR Decomposition */
  private Matrix Q;

  /** Upper-triangular matrix representation, M=QR, in QR Decomposition */
  private Matrix R;
  
  /** When calculating the inverse we calculate the LU matrices once */
  static private boolean calculatingInverse = false;
  
  /*
   * 
   * Define the constructors.
   * 
   *    
   */
  
  /** Create a Matrix that is a copy of another Matrix. */
  public Matrix(Matrix m) {
    this.m = new double[m.getNumberOfRows()][m.getNumberOfColumns()];
    for (int i=0; i<m.getNumberOfRows(); i++)
      for (int j=0; j<m.getNumberOfColumns(); j++)
        this.m[i][j] = m.getValue(i,j);
  }
  
  /** Create a {@code n} x {@code n} identity Matrix */
  public Matrix(int n) {
    m = new double[n][n];
    for (int i=0; i<n; i++) 
      m[i][i] = 1.0;
  }
  
  /** Create a {@code rows} x {@code cols} Matrix filled with zeros. */
  public Matrix(int rows, int cols) {
    m = new double[rows][cols];
  }

  /** Create a {@code rows} x {@code cols} Matrix filled with a value. */
  public Matrix(int rows, int cols, double value) {
    m = new double[rows][cols];
    for (int i=0; i<rows; i++)
      for (int j=0; j<cols; j++)
        m[i][j] = value;
  }

  /**
   * Create a {@code rows} x {@code cols} Matrix that is filled with 
   * uniformly-distributed random values that are within the range 
   * {@code min} to {@code max}.
   */
  public Matrix(int rows, int cols, double min, double max) {
    Random rand = new Random();
    m = new double[rows][cols];    
    for (int i=0; i<rows; i++)
      for (int j=0; j<cols; j++)        
        m[i][j] = (max-min)*rand.nextDouble()+min;
  }

  /** Create a Matrix from {@code m}. */
  public Matrix(Double[][] m) {    
    this.m = new double[m.length][m[0].length];
    for (int i=0; i<m.length; i++)
      for (int j=0; j<m[0].length; j++)        
        this.m[i][j] = m[i][j];
  }

  /** Create a Matrix from a vector. */
  public Matrix(Double[] vector) {
    m = new double[1][vector.length];
    for (int i=0; i<vector.length; i++)
      m[0][i] = vector[i];    
  }  

  /*
   * 
   * The public static methods.
   *
   * 
   */
  
  /** Returns the product of two Matrices as a new Matrix, C=AB. */
  public static Matrix multiply(Matrix a, Matrix b) {    
    if (a.getNumberOfColumns() != b.getNumberOfRows()) {
      throw new IllegalArgumentException(
          String.format("ERROR! Cannot multiply a %dx%d matrix "
            + "with a %dx%d matrix",
            a.getNumberOfRows(), a.getNumberOfColumns(),
            b.getNumberOfRows(), b.getNumberOfColumns()));
    } else {
      Matrix c = new Matrix(a.getNumberOfRows(), b.getNumberOfColumns());
      double sum = 0.0;
      for (int i = 0; i < a.getNumberOfRows() ; i++) {
        for (int j = 0; j < b.getNumberOfColumns(); j++) {
                 for (int k = 0 ; k < b.getNumberOfRows() ; k++) {
                    sum += a.getValue(i,k)*b.getValue(k,j);
                 }
                 c.setValue(i, j, sum);
                 sum = 0.0;
              }
           }
      return c;
    }
  }

  /** 
   * Solves {@code b = Ax} for {@code x}.
   * 
   * @param A - the coefficient matrix
   * @param b - the expected values
   * @return x - the solution to the system of equations
   */
  public static Matrix solve(Matrix A, Matrix b) {

    // ensure that 'b' is a column vector
    if (b.getNumberOfColumns() > 1)  b = b.transpose();
    
    // ensure that 'A' and 'b' have the correct dimensions
    if (b.getNumberOfRows() != A.getNumberOfRows()) {
      throw new IllegalArgumentException(
        String.format("ERROR! Dimension mismatch when solving the "
          + "system of equations using b=Ax, b has dimension "
          + " %dx%d and A is %dx%d.", b.getNumberOfRows(), 
          b.getNumberOfColumns(), A.getNumberOfRows(),
          A.getNumberOfColumns()));
    }

    // if A is an under-determined system of equations then use the 
    // matrix-multiplication expression to solve for x
    if (A.getNumberOfRows() < A.getNumberOfColumns()) {
      Matrix At = A.transpose();
      return Matrix.multiply(Matrix.multiply(At, 
          Matrix.multiply(A, At).getInverse() ), b);
    }
    
    // If A is a square matrix then use LU Decomposition, if it is an 
    // over-determined system of equations then use QR Decomposition
    Double[] x = new Double[A.getNumberOfColumns()];
    if (A.isSquare()) {
      
      // when using 'solve' to calculate the inverse of a matrix we
      // only need to generate the LU Decomposition matrices once
      if (!calculatingInverse) A.makeLU();
      
      // solve Ly=b for y using forward substitution
      double[] y = new double[b.getNumberOfRows()];
      y[0] = b.getValue(0,0);
      for (int i=1; i<y.length; i++) {
        y[i] = b.getValue(i,0);
        for (int j=0; j<i; j++)
          y[i] -= A.getL().getValue(i,j)*y[j];
      }
      
      // solve Ux=y for x using backward substitution
      for (int i=x.length-1; i>-1; i--) {
        x[i] = y[i];
        for (int j=i+1; j<x.length; j++)
          x[i] -= A.getU().getValue(i,j)*x[j];
        x[i] /= A.getU().getValue(i,i);
      }
      
    } else {
      
      A.makeQR();
      Matrix d = Matrix.multiply(A.getQ().transpose(), b);

      // solve Rx=d for x using backward substitution
      for (int i=x.length-1; i>-1; i--) {
        x[i] = d.getValue(i, 0);
        for (int j=i+1; j<x.length; j++)
          x[i] -= A.getR().getValue(i,j)*x[j];
        x[i] /= A.getR().getValue(i,i);
      }      
    }    
    
    return new Matrix(x).transpose();
  }

  /*
   * 
   * The public methods.
   *
   * 
   */

  /** Returns the primitive data of the Matrix. */
  public double[][] primitive() {
    return m;
  }
  
  /** Convert the Matrix to a string. */
  @Override
  public String toString() {
    StringBuffer sb = new StringBuffer();
    for (int i=0; i<m.length; i++) {
      for (int j=0; j<m[0].length; j++) {
        sb.append(String.format("%+.6e\t", m[i][j]));
      }
      sb.append("\n");
    }
    return sb.toString();
  }

  /** Returns the number of rows in the Matrix. */
  public int getNumberOfRows() {
    return m.length;
  }

  /** Returns the number of columns in the Matrix. */
  public int getNumberOfColumns() {
    try {
      return m[0].length; 
    } catch (ArrayIndexOutOfBoundsException e) {
      return 0;
    }
  }
  
  /** Returns the value at {@code row} and {@code col}. */
  public double getValue(int row, int col) {
    return m[row][col];
  }

  /** Sets the value at {@code row} and {@code col} to be {@code value}. */
  public void setValue(int row, int col, double value) {
    m[row][col] = value;
  }  

  /** Returns the transpose of the Matrix. */
  public Matrix transpose() {
    Matrix mt = new Matrix(m[0].length, m.length);
    for (int i=0; i<m.length; i++)
      for (int j=0; j<m[0].length; j++)
        mt.setValue(j, i, m[i][j]);
    return mt;
  }

  /** Returns whether the Matrix is a square Matrix. */
  public boolean isSquare() {
    return m.length == m[0].length;
  }
  
  /** Returns the determinant of the Matrix. */
  public double getDeterminant() {
    if (isSquare()) {
      makeLU();
      double det = 1.0;
      for (int i=0; i<m.length; i++)
        det *= U.getValue(i,i);
      // 's' is the number of row and column exchanges in LU Decomposition
      // but we are currently not using pivoting
      int s = 0;
      return Math.pow(-1.0, s)*det;
    } else {
      return Double.NaN;
    }
  }
  
  /** Returns the lower-triangular Matrix, L, from a LU Decomposition */
  public Matrix getL() {
    if (L==null) makeLU();
    return L;
  }
  
  /** Returns the upper-triangular Matrix, U, from a LU Decomposition */
  public Matrix getU() {
    if (U==null) makeLU();
    return U;
  }

  /** Returns the orthogonal Matrix, Q, from a QR Decomposition */
  public Matrix getQ() {
    if (Q==null) makeQR();
    return Q;
  }
  
  /** Returns the upper-triangular Matrix, R, from a QR Decomposition */
  public Matrix getR() {
    if (R==null) makeQR();
    return R;
  }

  /** Returns the inverse of the Matrix, if it exists. */
  public Matrix getInverse() {
    if (isSquare()) {
      Matrix inv = new Matrix(m.length);
      Matrix bb = new Matrix(m.length);
      for (int i=0; i<m.length; i++) {
        inv.setColumn(i, Matrix.solve(this, bb.getColumn(i)));
        calculatingInverse = true;
      }
      calculatingInverse = false;
      return inv;
    } else {
      throw new IllegalArgumentException(
        String.format("ERROR! Cannot calculate the inverse of a "
          + "%dx%d matrix, it must be a square Matrix", 
          m.length, m[0].length));
    }
  }

  
  /*
   * 
   * Private methods.
   * 
   * 
   */

  /** 
   * Create the Lower, L, and Upper, U, triangular matrices, such that M=LU.
   * Does not use pivoting. 
   */
  private void makeLU() {
    L = new Matrix(m.length); // create an identity matrix
    U = new Matrix(this); // copy the values of this matrix
    double val;
    for (int k=0; k<m[0].length; k++) {
      for (int i=k+1; i<m.length; i++) {
        val = U.getValue(i,k)/U.getValue(k,k);
        L.setValue(i, k, val);
        for (int j=k; j<m[0].length; j++)
          U.setValue(i, j, U.getValue(i,j)-val*U.getValue(k,j));
      }
    }    
  }

  /** 
   * Computes the QR Factorization matrices using a modified 
   * Gram–Schmidt process.<p>
   * 
   * @see http://www.inf.ethz.ch/personal/gander/papers/qrneu.pdf
   */
  private void makeQR() {
    
    Q = new Matrix(m.length, m[0].length);
    R = new Matrix(m[0].length, m[0].length);
    Matrix A = new Matrix(this);
    
    double s;
    for (int k=0; k<m[0].length; k++) {
      s = 0.0;
      for (int j=0; j<m.length; j++)
        s += Math.pow(A.getValue(j, k), 2);
      s = Math.sqrt(s);
      R.setValue(k, k, s);
      for (int j=0; j<m.length; j++)
        Q.setValue(j, k, A.getValue(j, k)/s);
      for (int i=k+1; i<m[0].length; i++) {
        s = 0.0;
        for (int j=0; j<m.length; j++)
          s += A.getValue(j, i)*Q.getValue(j, k);
        R.setValue(k, i, s);
        for (int j=0; j<m.length; j++)
          A.setValue(j, i, A.getValue(j,i)-R.getValue(k,i)*Q.getValue(j,k));
      }
    }
  }

  /** Returns a copy of the specified column. */
  private Matrix getColumn(int column) {
    if (column < m[0].length) {
      Matrix c = new Matrix(m.length, 1);
      for (int i=0; i<m.length; i++)
        c.setValue(i, 0, m[i][column]);
      return c;
    } else {
      throw new IllegalArgumentException(
        String.format("ERROR! Cannot get column %d in the Matrix "
          + "since it is > the number of columns in the "
          + "Matrix, %d.", column, m[0].length));
    }
  }

  /** 
   * Replace the values in the specified column of the matrix to the values in
   * {@code vector}.
   *  
   * The {@code vector} must be a 1D vector, can have dimension 1xN or Nx1.
   */
  private void setColumn(int column, Matrix vector) {
    
    // make sure that 'vector' is either a 1xN or Nx1 vector and not a NxM Matrix
    if ( (vector.getNumberOfColumns() != 1) && (vector.getNumberOfRows() != 1) ) {
      throw new IllegalArgumentException(
        String.format("ERROR! Require a 1D vector to replace the values "
          + "in a column of a matrix. Got a %dx%d vector.", 
          vector.getNumberOfRows(), vector.getNumberOfColumns()));
    }
    
    // make sure we have a column vector
    if (vector.getNumberOfColumns() != 1) {
      vector = vector.transpose();
    }
    
    // make sure the 'vector' has the correct length
    if (vector.getNumberOfRows() != m.length) {
      throw new IllegalArgumentException(
        String.format("ERROR! Cannot replace a Matrix column of length "
          + "%d, with a column vector of length %d.",
          m.length, vector.getNumberOfRows()));
    }

    // make sure the column is valid
    if (column >= m[0].length) {
      throw new IllegalArgumentException(
        String.format("ERROR! Cannot replace column %d in the Matrix "
        + "since it is > the number of columns in the matrix.", column));
    }

    for (int i=0; i<m.length; i++)
      m[i][column] = vector.getValue(i,0);
  }

}
