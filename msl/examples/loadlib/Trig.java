/*
 * Compile with JDK 6 for maximal compatibility with Py4J
 * 
 * javac Trig.java
 *
 */

public class Trig {
  
  /** Returns the trigonometric cosine of an angle. */
  static public double cos(double x) {
    return Math.cos(x);
  }

  /** Returns the hyperbolic cosine of a value. */
  static public double cosh(double x) {
    return Math.cosh(x);
  }

  /** Returns the arc cosine of a value, [0.0, pi]. */
  static public double acos(double x) {
    return Math.acos(x);
  }

  /** Returns the trigonometric sine of an angle. */
  static public double sin(double x) {
    return Math.sin(x);
  }

  /** Returns the hyperbolic sine of a value. */
  static public double sinh(double x) {
    return Math.sinh(x);
  }

  /** Returns the arc sine of a value, [-pi/2, pi/2]. */
  static public double asin(double x) {
    return Math.asin(x);
  }

  /** Returns the trigonometric tangent of an angle. */
  static public double tan(double x) {
    return Math.tan(x);
  }

  /** Returns the hyperbolic tangent of a value. */
  static public double tanh(double x) {
    return Math.tanh(x);
  }

  /** Returns the arc tangent of a value; [-pi/2, pi/2]. */
  static public double atan(double x) {
    return Math.atan(x);
  }

  /** 
   * Returns the angle theta from the conversion of rectangular coordinates 
   * (x, y) to polar coordinates (r, theta).
   */
  static public double atan2(double y, double x) {
    return Math.atan2(y, x);
  }

}
