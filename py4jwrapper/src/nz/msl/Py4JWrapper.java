package nz.msl;

import java.io.File;
import java.lang.NoSuchMethodException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.IllegalAccessException;
import java.net.MalformedURLException;
import java.net.URLClassLoader;
import java.net.URL;

import py4j.GatewayServer;

public class Py4JWrapper {

	public static void main(String[] args) throws ClassNotFoundException, InstantiationException, 
												  IllegalAccessException, MalformedURLException {
		int port = Integer.parseInt(args[0]);
		File jar = new File(args[1]);
		
		URL url = new URL("jar", "", "file:" + jar.getAbsolutePath() + "!/");

		if (loadLibrary(url)) {    	
			GatewayServer server = new GatewayServer(null, port);
			server.start();
		}	
		
	}

	public static boolean loadLibrary(URL url) {
		URLClassLoader sysLoader = (URLClassLoader)ClassLoader.getSystemClassLoader();
		
		try {
			Method sysMethod = URLClassLoader.class.getDeclaredMethod("addURL",new Class[] {URL.class});
			sysMethod.setAccessible(true);
			sysMethod.invoke(sysLoader, new Object[]{url});
			return true;
		} catch (NoSuchMethodException | SecurityException | IllegalAccessException | 
				IllegalArgumentException | InvocationTargetException e) {
			return false;
		}

	}
	
}
