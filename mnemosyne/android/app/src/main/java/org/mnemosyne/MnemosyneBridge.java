package org.mnemosyne;

import org.json.JSONObject;
import org.json.JSONException;

import android.util.Log;

import org.mnemosyne.PyBridge;

public class MnemosyneBridge {

    public MnemosyneBridge() {
        PyBridge.start(basedir + "/assets/python", UIActivity);
        Log.d("Mnemosyne", "Started pybridge");
    }

    public void startMnemosyne(String data_dir, String filename) {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "start_mnemosyne");
            json.put("data_dir", data_dir);
            json.put("filename", filename);
            JSONObject result = PyBridge.call(json);
            Log.i("Mnemosyne", "started Mnemosyne");
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public void pauseMnemosyne()
    {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "pauze_mnemosyne");
            JSONObject result = PyBridge.call(json);
            Log.i("Mnemosyne", "paused Mnemosyne");
        } catch (JSONException e) {
            e.printStackTrace();
        }
        PyBridge.stop();
    }

    public void stopMnemosyne()
    {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "stop_mnemosyne");
            JSONObject result = PyBridge.call(json);
            Log.i("Mnemosyne", "stopped Mnemosyne");
        } catch (JSONException e) {
            e.printStackTrace();
        }
        PyBridge.stop();
    }


    public void controller_heartbeat() {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "controller_heartbeat");
            json.put("db_maintenance", false)
            JSONObject result = PyBridge.call(json);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }
}
