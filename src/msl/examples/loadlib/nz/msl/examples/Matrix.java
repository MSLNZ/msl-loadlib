package nz.msl.examples;

import java.util.Random;

/**
 * A simple Matrix class supporting basic operations:
 * multiplication, solving linear systems, LU decomposition
 * with partial pivoting, QR decomposition, inversion, etc.
 */
public class Matrix {

    /** The matrix data */
    private double[][] m;

    /** Lower-triangular matrix in LU, M = L⋅U */
    private Matrix L;

    /** Upper-triangular matrix in LU, M = L⋅U */
    private Matrix U;

    /** Orthogonal matrix in QR, M = Q⋅R */
    private Matrix Q;

    /** Upper-triangular matrix in QR, M = Q⋅R */
    private Matrix R;

    /** Number of row swaps performed during LU (for determinant sign) */
    private int pivotCount = 0;

    /** When calculating inverse we reuse LU; avoid repeated pivots */
    static private boolean calculatingInverse = false;

    // ==== Constructors ====

    /** Copy constructor */
    public Matrix(Matrix m) {
        this.m = new double[m.getNumberOfRows()][m.getNumberOfColumns()];
        for (int i = 0; i < m.getNumberOfRows(); i++)
            for (int j = 0; j < m.getNumberOfColumns(); j++)
                this.m[i][j] = m.getValue(i, j);
    }

    /** Identity matrix (n×n) */
    public Matrix(int n) {
        m = new double[n][n];
        for (int i = 0; i < n; i++)
            m[i][i] = 1.0;
    }

    /** Zero matrix (rows×cols) */
    public Matrix(int rows, int cols) {
        m = new double[rows][cols];
    }

    /** Constant-filled matrix */
    public Matrix(int rows, int cols, double value) {
        m = new double[rows][cols];
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++)
                m[i][j] = value;
    }

    /** Random uniform(min–max) matrix */
    public Matrix(int rows, int cols, double min, double max) {
        Random rand = new Random();
        m = new double[rows][cols];
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++)
                m[i][j] = (max - min) * rand.nextDouble() + min;
    }

    /** From Double[][] */
    public Matrix(Double[][] m) {
        this.m = new double[m.length][m[0].length];
        for (int i = 0; i < m.length; i++)
            for (int j = 0; j < m[0].length; j++)
                this.m[i][j] = m[i][j];
    }

    /** From Double[] vector (1×N) */
    public Matrix(Double[] vector) {
        m = new double[1][vector.length];
        for (int i = 0; i < vector.length; i++)
            m[0][i] = vector[i];
    }

    // ==== Public static operations ====

    /** C = A⋅B */
    public static Matrix multiply(Matrix a, Matrix b) {
        if (a.getNumberOfColumns() != b.getNumberOfRows()) {
            throw new IllegalArgumentException(
                String.format("Cannot multiply %dx%d by %dx%d",
                    a.getNumberOfRows(), a.getNumberOfColumns(),
                    b.getNumberOfRows(), b.getNumberOfColumns()));
        }
        Matrix c = new Matrix(a.getNumberOfRows(), b.getNumberOfColumns());
        for (int i = 0; i < a.getNumberOfRows(); i++) {
            for (int j = 0; j < b.getNumberOfColumns(); j++) {
                double sum = 0.0;
                for (int k = 0; k < b.getNumberOfRows(); k++) {
                    sum += a.getValue(i, k) * b.getValue(k, j);
                }
                c.setValue(i, j, sum);
            }
        }
        return c;
    }

    /**
     * Solve b = A x for x
     */
    public static Matrix solve(Matrix A, Matrix b) {
        if (b.getNumberOfColumns() > 1) b = b.transpose();
        if (b.getNumberOfRows() != A.getNumberOfRows()) {
            throw new IllegalArgumentException("Dimension mismatch in solve()");
        }
        if (A.getNumberOfRows() < A.getNumberOfColumns()) {
            Matrix At = A.transpose();
            return multiply(multiply(At, multiply(A, At).getInverse()), b);
        }

        Double[] x = new Double[A.getNumberOfColumns()];
        if (A.isSquare()) {
            if (!calculatingInverse) A.makeLU();
            // forward substitute Ly = b
            double[] y = new double[b.getNumberOfRows()];
            y[0] = b.getValue(0, 0);
            for (int i = 1; i < y.length; i++) {
                y[i] = b.getValue(i, 0);
                for (int j = 0; j < i; j++)
                    y[i] -= A.getL().getValue(i, j) * y[j];
            }
            // backward substitute Ux = y
            for (int i = x.length - 1; i >= 0; i--) {
                x[i] = y[i];
                for (int j = i + 1; j < x.length; j++)
                    x[i] -= A.getU().getValue(i, j) * x[j];
                x[i] /= A.getU().getValue(i, i);
            }
        } else {
            A.makeQR();
            Matrix d = multiply(A.getQ().transpose(), b);
            for (int i = x.length - 1; i >= 0; i--) {
                x[i] = d.getValue(i, 0);
                for (int j = i + 1; j < x.length; j++)
                    x[i] -= A.getR().getValue(i, j) * x[j];
                x[i] /= A.getR().getValue(i, i);
            }
        }
        return new Matrix(x).transpose();
    }

    // ==== Public instance methods ====

    public double[][] primitive() { return m; }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        for (double[] row : m) {
            for (double v : row) {
                sb.append(String.format("%+.6e\t", v));
            }
            sb.append("\n");
        }
        return sb.toString();
    }

    public int getNumberOfRows() { return m.length; }
    public int getNumberOfColumns() {
        return (m.length == 0) ? 0 : m[0].length;
    }
    public double getValue(int row, int col) { return m[row][col]; }
    public void setValue(int row, int col, double value) { m[row][col] = value; }
    public boolean isSquare() { return m.length == m[0].length; }

    public Matrix transpose() {
        Matrix t = new Matrix(m[0].length, m.length);
        for (int i = 0; i < m.length; i++)
            for (int j = 0; j < m[0].length; j++)
                t.setValue(j, i, m[i][j]);
        return t;
    }

    // ==== LU with Partial Pivoting ====

    /**
     * Builds L and U with partial pivoting: M = P⋅L⋅U.
     * We track the number of row swaps in pivotCount.
     */
    private void makeLU() {
        int n = m.length;
        L = new Matrix(n);
        U = new Matrix(this);
        pivotCount = 0;

        for (int k = 0; k < n; k++) {
            // find pivot row
            int pivot = k;
            double max = Math.abs(U.getValue(k, k));
            for (int i = k + 1; i < n; i++) {
                double v = Math.abs(U.getValue(i, k));
                if (v > max) {
                    max = v; pivot = i;
                }
            }
            // swap rows if needed
            if (pivot != k) {
                swapRows(U.m, k, pivot);
                swapRows(L.m, k, pivot, k);
                pivotCount++;
            }
            // elimination
            for (int i = k + 1; i < n; i++) {
                double factor = U.getValue(i, k) / U.getValue(k, k);
                L.setValue(i, k, factor);
                for (int j = k; j < n; j++) {
                    U.setValue(i, j, U.getValue(i, j) - factor * U.getValue(k, j));
                }
            }
        }
    }

    /** Swap two entire rows in a 2D array */
    private void swapRows(double[][] A, int r1, int r2) {
        double[] tmp = A[r1];
        A[r1] = A[r2];
        A[r2] = tmp;
    }

    /** Swap two rows up to a given column in L (to preserve previous L entries) */
    private void swapRows(double[][] A, int r1, int r2, int uptoCol) {
        for (int j = 0; j < uptoCol; j++) {
            double tmp = A[r1][j];
            A[r1][j] = A[r2][j];
            A[r2][j] = tmp;
        }
    }

    /** Returns the lower-triangular factor L */
    public Matrix getL() {
        if (L == null) makeLU();
        return L;
    }

    /** Returns the upper-triangular factor U */
    public Matrix getU() {
        if (U == null) makeLU();
        return U;
    }

    /** Compute determinant = (−1)^pivotCount × ∏ diagonal(U) */
    public double getDeterminant() {
        if (!isSquare()) return Double.NaN;
        makeLU();
        double det = Math.pow(-1.0, pivotCount);
        for (int i = 0; i < m.length; i++) {
            det *= U.getValue(i, i);
        }
        return det;
    }

    // ==== QR Decomposition ====

    private void makeQR() {
        int rows = m.length, cols = m[0].length;
        Q = new Matrix(rows, cols);
        R = new Matrix(cols, cols);
        Matrix A = new Matrix(this);

        for (int k = 0; k < cols; k++) {
            double norm = 0;
            for (int i = 0; i < rows; i++) norm += A.getValue(i, k) * A.getValue(i, k);
            norm = Math.sqrt(norm);
            R.setValue(k, k, norm);
            for (int i = 0; i < rows; i++) {
                Q.setValue(i, k, A.getValue(i, k) / norm);
            }
            for (int j = k + 1; j < cols; j++) {
                double dot = 0;
                for (int i = 0; i < rows; i++) {
                    dot += A.getValue(i, j) * Q.getValue(i, k);
                }
                R.setValue(k, j, dot);
                for (int i = 0; i < rows; i++) {
                    A.setValue(i, j, A.getValue(i, j) - dot * Q.getValue(i, k));
                }
            }
        }
    }

    public Matrix getQ() {
        if (Q == null) makeQR();
        return Q;
    }

    public Matrix getR() {
        if (R == null) makeQR();
        return R;
    }

    /** Returns the inverse via repeated solves */
    public Matrix getInverse() {
        if (!isSquare()) {
            throw new IllegalArgumentException("Cannot invert non-square matrix");
        }
        Matrix inv = new Matrix(m.length);
        Matrix e = new Matrix(m.length); // identity columns
        calculatingInverse = true;
        for (int i = 0; i < m.length; i++) {
            inv.setColumn(i, solve(this, e.getColumn(i)));
        }
        calculatingInverse = false;
        return inv;
    }

    // ==== Helper for inverse ====

    /** Extract column as vector */
    private Matrix getColumn(int col) {
        Matrix c = new Matrix(m.length, 1);
        for (int i = 0; i < m.length; i++) {
            c.setValue(i, 0, m[i][col]);
        }
        return c;
    }

    /** Replace column */
    private void setColumn(int col, Matrix vector) {
        if (vector.getNumberOfColumns() != 1 && vector.getNumberOfRows() != 1) {
            throw new IllegalArgumentException("Vector must be 1D");
        }
        if (vector.getNumberOfColumns() != 1) {
            vector = vector.transpose();
        }
        if (vector.getNumberOfRows() != m.length) {
            throw new IllegalArgumentException("Column length mismatch");
        }
        for (int i = 0; i < m.length; i++) {
            m[i][col] = vector.getValue(i, 0);
        }
    }
}
