package org.mnemosyne;

import com.srplab.www.starcore.StarCoreFactory;
import com.srplab.www.starcore.StarCoreFactoryPath;
import com.srplab.www.starcore.StarObjectClass;
import com.srplab.www.starcore.StarServiceClass;
import com.srplab.www.starcore.StarSrvGroupClass;

import android.os.Handler;
import android.os.Looper;
import android.util.Log;


public class MnemosyneThread extends Thread {

    StarObjectClass python;
    StarObjectClass mnemosyne;
    StarObjectClass reviewController;
    MnemosyneActivity UIActivity;
    Handler mnemosyneHandler = new Handler();
    Handler UIHandler;
    String basedir;

    public MnemosyneThread(MnemosyneActivity activity, Handler handler, String packageName) {
        UIActivity = activity;
        UIHandler = handler;
        basedir = "/data/data/" + packageName;
    }

    public Handler getHandler() {
        return mnemosyneHandler;
    }

    public void startMnemosyne() {
        StarCoreFactoryPath.StarCoreCoreLibraryPath = basedir + "/lib";
        StarCoreFactoryPath.StarCoreShareLibraryPath = basedir + "/lib";
        StarCoreFactoryPath.StarCoreOperationPath = basedir + "/files";
        StarCoreFactory starcore = StarCoreFactory.GetFactory();

        Log.d("Mnemosyne", "Initialising starcore");

        StarSrvGroupClass SrvGroup = starcore._GetSrvGroup(0);
        StarServiceClass Service = SrvGroup._GetService("cle", "123");
        if (Service == null) {  // The service has not been initialized.
            Service = starcore._InitSimple("cle", "123", 0, 0);
            Service._CheckPassword(false);
            SrvGroup = (StarSrvGroupClass) Service._Get("_ServiceGroup");
            SrvGroup._InitRaw("python", Service);
            python = Service._ImportRawContext("python", "", false, "");

            // Set up extra paths.
            python._Call("import", "sys");
            StarObjectClass pythonSys = python._GetObject("sys");
            StarObjectClass pythonPath = (StarObjectClass) pythonSys._Get("path");
            pythonPath._Call("insert", 0, basedir + "/files/python_extras_r14.zip");
            pythonPath._Call("insert", 0, basedir + "/lib");
            pythonPath._Call("insert", 0, basedir + "/files/lib-dynload");
            pythonPath._Call("insert", 0, basedir + "/files");

            Log.d("Mnemosyne", "about to start Mnemosyne");

            // Start Mnemosyne.
            SrvGroup._LoadRawModule("python", "", basedir +
                    "/files/mnemosyne/cle/mnemosyne_android.py", false);
            mnemosyne = python._GetObject("mnemosyne");

            String dataDir = "/sdcard/Mnemosyne/";
            String filename = "default.db";
            StarObjectClass activity = Service._New();
            activity._AttachRawObject(this, false);

            python._Call("start_mnemosyne", dataDir, filename, this);

            reviewController = (StarObjectClass) mnemosyne._Call("review_controller");

            Log.d("Mnemosyne", "started Mnemosyne");
        }
    }

    @Override
    public void run() {
        Log.d("Mnemosyne", "starting running Mnemosyne thread");
        startMnemosyne();

        Looper.prepare();
        Looper.loop();
    }

    public void setQuestionLabel(String label) {
        final String _label = label;
        UIHandler.post(new Runnable() {
            public void run() {
                UIActivity.questionLabel.setText(_label);
            }
        });
    }

    public void setStatusbarText(String text) {
        final String _text = text;
        UIHandler.post(new Runnable() {
            public void run() {
                UIActivity.statusbar.setText(_text);
            }
        });
    }

}