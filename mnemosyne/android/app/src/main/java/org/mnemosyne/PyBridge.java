package org.mnemosyne;

import android.util.Log;

import org.json.JSONObject;
import org.json.JSONException;


// Based on code from https://github.com/joaoventura/pybridge.

public class PyBridge {

    private static MnemosyneActivity _activity;

    public static int initialise(String asset_path, String library_path, MnemosyneActivity activity,
                                 MnemosyneThread thread) {
        _activity = activity;
        return start(asset_path, library_path, thread);
    }

    /**
     * Initializes the Python interpreter.
     *
     * @param asset_path the location of the Python files
     * @param library_path the location of the native compiled libraries
     * @return error code
     */
    public static native int start(String asset_path, String library_path, MnemosyneThread thread);

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
            JSONObject JSONresult = new JSONObject(result);
            if (JSONresult.getString("status").equals("fail")) {
                String msg = "Internal error. Please forward this information to the developers:\n\n"
                        + JSONresult.getString("result");
                _activity.mnemosyneThread.showInformation(msg);
                return null;
            }
            return JSONresult;
        } catch (JSONException e) {
            e.printStackTrace();
            return null;
        }
    }

    // Load library.
    static {
        System.loadLibrary("pybridge");
        Log.i("Mnemosyne", "Pybridge loaded");
    }
}
