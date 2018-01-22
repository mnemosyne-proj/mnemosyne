package org.mnemosyne;

import org.json.JSONObject;
import org.json.JSONException;

import android.util.Log;

import org.mnemosyne.PyBridge;

public class MnemosyneBridge {

    public MnemosyneBridge(String basedir, MnemosyneActivity UIActivity) {
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
            json.put("db_maintenance", false);
            JSONObject result = PyBridge.call(json);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public String config_get(String key) {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "config_get");
            json.put("key", key);
            JSONObject result = PyBridge.call(json);
            return result.getString("result");
        } catch (JSONException e) {
            e.printStackTrace();
            return "";
        }
    }

    public void review_controller_show_answer() {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "review_controller_show_answer");
            JSONObject result = PyBridge.call(json);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public void review_controller_grade_answer(int grade) {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "review_controller_grade_answer");
            json.put("grade", grade);
            JSONObject result = PyBridge.call(json);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public void controller_show_sync_dialog_pre() {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "controller_show_sync_dialog_pre");
            JSONObject result = PyBridge.call(json);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public void controller_star_current_card() {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "controller_star_current_card");
            JSONObject result = PyBridge.call(json);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public void controller_show_activate_cards_dialog_pre() {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "show_activate_cards_dialog_pre");
            JSONObject result = PyBridge.call(json);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }
}
