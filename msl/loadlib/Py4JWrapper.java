/*
 * Use JDK 6 for maximal compatibility with Py4J
 * 
 * cd msl-loadlib/msl/loadlib/
 * javac -cp <env-dir>\share\py4j\py4j0.10.6.jar Py4JWrapper.java
 * jar cfv py4j-wrapper.jar Py4JWrapper.class
 *
 */
import java.net.URL;
import java.net.URLClassLoader;
import java.net.MalformedURLException;

import py4j.GatewayServer;

public class Py4JWrapper {

    public static void main(String[] args) throws MalformedURLException {
        int port = Integer.parseInt(args[0]);
        URL url = new URL("file:" + args[1]);
        URLClassLoader loader = new URLClassLoader(new URL[]{url});
        Thread.currentThread().setContextClassLoader(loader);
        GatewayServer server = new GatewayServer(null, port);
        server.start();
    }

}
