package org.mnemosyne;

import org.json.JSONObject;
import org.json.JSONException;

import android.util.Log;

import java.io.File;

public class MnemosyneBridge {

    private MnemosyneActivity UIActivity;

    public MnemosyneBridge(String basedir, MnemosyneActivity UIActivity, MnemosyneThread thread) {
        // Older Android versions (e.g. 4.4) cannot dynamically load libraries, so we
        // preload them all here.

        // File from = new File(UIActivity.getApplicationInfo().nativeLibraryDir, "md5.cpython-37m.so");
        // File to = new File(UIActivity.getApplicationInfo().nativeLibraryDir,"_md5.cpython-37m.so");
        // from.renameTo(to);
        // Log.d("Mnemosyne", "Renamed");

        Log.d("Mnemosyne", "nativelibrarydir" + UIActivity.getApplicationInfo().nativeLibraryDir );

        String path = UIActivity.getApplicationInfo().nativeLibraryDir;
        Log.d("Files", "Path: " + path);
        File directory = new File(path);
        File[] files = directory.listFiles();
        Log.d("Files", "Size: "+ files.length);
        for (int i = 0; i < files.length; i++)
        {
            Log.d("Files", "FileName:" + files[i].getName());
        }

        //System.load(UIActivity.getApplicationInfo().nativeLibraryDir + "/modules/binascii.cpython-37m.so");
        //System.load(UIActivity.getApplicationInfo().nativeLibraryDir + "/libpython3.7m.so");

        // Does not seem to work in trying to preload the libraries, so that we can use an app bundle.
        //System.load(UIActivity.getApplicationInfo().nativeLibraryDir + "/zlib.cpython-37m.so");
        //System.load(basedir + "/assets/python/select.so");
        //System.load(basedir + "/assets/python/unicodedata.so");
        //System.load(basedir + "/assets/python/_socket.so");
        //System.load(basedir + "/assets/python/_sqlite3.so");
        //System.load(basedir + "/assets/python/pyexpat.so");
        //Log.d("Mnemosyne", "Preloaded libraries");

        PyBridge.initialise(basedir + "/assets/python",
                UIActivity.getApplicationInfo().nativeLibraryDir, UIActivity, thread);
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
            json.put("function", "pause_mnemosyne");
            JSONObject result = PyBridge.call(json);
            Log.i("Mnemosyne", "paused Mnemosyne");
        } catch (JSONException e) {
            e.printStackTrace();
        }
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

    public void config_set_string(String key, String value) {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "config_set");
            json.put("key", key);
            json.put("value", value);
            JSONObject result = PyBridge.call(json);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public void config_set_integer(String key, Integer value) {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "config_set");
            json.put("key", key);
            json.put("value", value);
            JSONObject result = PyBridge.call(json);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public void config_save() {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "config_save");
            JSONObject result = PyBridge.call(json);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public void controller_heartbeat() {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "controller_heartbeat");
            json.put("db_maintenance", true);
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

    public void controller_sync(String server, Integer port,
                                String username, String password) {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "controller_sync");
            json.put("server", server);
            json.put("port", port);
            json.put("username", username);
            json.put("password", password);
            JSONObject result = PyBridge.call(json);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public void controller_show_sync_dialog_post() {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "controller_show_sync_dialog_post");
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
            json.put("function", "controller_show_activate_cards_dialog_pre");
            JSONObject result = PyBridge.call(json);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public void controller_show_activate_cards_dialog_post() {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "controller_show_activate_cards_dialog_post");
            JSONObject result = PyBridge.call(json);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public void controller_set_study_mode_with_id(String id) {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "controller_set_study_mode_with_id");
            json.put("id", id);
            JSONObject result = PyBridge.call(json);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public void controller_do_db_maintenance() {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "controller_do_db_maintenance");
            JSONObject result = PyBridge.call(json);
        } catch (JSONException e) {
            e.printStackTrace();
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

    public void database_set_criterion_with_name(String savedSet) {
        try {
            JSONObject json = new JSONObject();
            json.put("function", "database_set_criterion_with_name");
            json.put("saved_set", savedSet);
            JSONObject result = PyBridge.call(json);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }
}
