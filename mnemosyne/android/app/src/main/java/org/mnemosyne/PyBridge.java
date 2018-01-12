package org.mnemosyne;

import org.mnemosyne.MnemosyneActivity;

import org.json.JSONObject;
import org.json.JSONException;


// Based on code from https://github.com/joaoventura/pybridge.

public class PyBridge {

    /**
     * Initializes the Python interpreter.
     *
     * @param datapath the location of the extracted python files
     * @return error code
     */
    public static native int start(String datapath, MnemosyneActivity activity);

    /**
     * Stops the Python interpreter.
     *
     * @return error code
     */
    public static native int stop();

    /**
     * Sends a string payload to the Python interpreter.
     *
     * @param payload the payload string
     * @return a string with the result
     */
    public static native String call(String payload);

    /**
     * Sends a JSON payload to the Python interpreter.
     *
     * @param payload JSON payload
     * @return JSON response
     */
    public static JSONObject call(JSONObject payload) {
        String result = call(payload.toString());
        try {
            return new JSONObject(result);
        } catch (JSONException e) {
            e.printStackTrace();
            return null;
        }
    }

    // Load library
    static {
        System.loadLibrary("pybridge");
    }
}
