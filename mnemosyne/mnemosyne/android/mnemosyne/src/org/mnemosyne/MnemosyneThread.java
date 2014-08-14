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
    Handler mnemosyneHandler = new Handler();
    Handler activityHandler;
    String basedir;

    public MnemosyneThread(Handler handler, String packageName) {
        activityHandler = handler;
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

            // Start Mnemosyne.
            SrvGroup._LoadRawModule("python", "", basedir +
                    "/files/mnemosyne/cle/mnemosyne_android.py", false);
            mnemosyne = python._GetObject("mnemosyne");

            String dataDir = "/sdcard/Mnemosyne/";
            String filename = "default.db";
            StarObjectClass activity = Service._New();
            activity._AttachRawObject(this, false);

            python._Call("start_mnemosyne", dataDir, filename, activity);

            reviewController = (StarObjectClass) mnemosyne._Call("review_controller");
        }
    }

    @Override
    public void run() {
        startMnemosyne();

        Looper.prepare();
        Looper.loop();

        Log.d("Mnemosyne", "done_thread ");
    }

}