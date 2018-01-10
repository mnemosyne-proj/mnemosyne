package org.mnemosyne;

import android.app.AlertDialog;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.app.ProgressDialog;
import android.os.AsyncTask;
import android.os.Handler;
import android.util.Log;

import java.io.File;
import java.io.FileWriter;
import java.io.FileReader;
import java.io.FileOutputStream;
import java.io.BufferedWriter;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;

public class MnemosyneInstaller extends AsyncTask<Void, Void, Void>  {

    private MnemosyneActivity UIActivity;
    private String basedir;
    Handler UIHandler;
    private static String mAssetModifiedPath = "lastmodified.txt";

    public MnemosyneInstaller(MnemosyneActivity activity, Handler handler)
    {
        UIActivity = activity;
        UIHandler = handler;
        basedir = UIActivity.getApplicationInfo().dataDir;
    }

    private void setAssetLastModified(long time) {
        String filename = basedir + mAssetModifiedPath;
        try {
            BufferedWriter bwriter = new BufferedWriter(new FileWriter(new File(filename)));
            bwriter.write(String.format("%d", time));
            bwriter.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private long getAssetLastModified() {
        String filename = basedir + mAssetModifiedPath;
        try {
            BufferedReader breader = new BufferedReader(new FileReader(new File(filename)));
            String contents = breader.readLine();
            breader.close();
            return Long.valueOf(contents).longValue();
        } catch (IOException e) {
            Log.d("Mnemosyne", filename + " does not exist.");
            return 0;
        }
    }

    private long getAppLastUpdate() {
        PackageManager pm = UIActivity.getPackageManager();
        try {
            PackageInfo pkgInfo = pm.getPackageInfo(UIActivity.getPackageName(),
                    PackageManager.GET_PERMISSIONS);
            return pkgInfo.lastUpdateTime;
        } catch (Exception e) {
            e.printStackTrace();
            return 1;
        }
    }

    private void copyAssetFile(String src, String dst) {
        File file = new File(dst);
        Log.i("Mnemosyne", String.format("Copying %s -> %s", src, dst));
        try {
            File dir = file.getParentFile();
            if (!dir.exists()) {
                dir.mkdirs();
            }
            InputStream in = UIActivity.getAssets().open(src);
            OutputStream out = new FileOutputStream(file);
            byte[] buffer = new byte[1024];
            int read = in.read(buffer);
            while (read != -1) {
                out.write(buffer, 0, read);
                read = in.read(buffer);
            }
            out.close();
            in.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public List<String> listAssets(String path) {
        List<String> assets = new ArrayList<>();

        try {
            String assetList[] = UIActivity.getAssets().list(path);
            if (assetList.length > 0) {
                for (String asset : assetList) {
                    List<String> subAssets = listAssets(path + '/' + asset);
                    assets.addAll(subAssets);
                }
            } else {
                assets.add(path);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return assets;
    }

    public void copyAssets(String path) {
        for (String asset : listAssets(path)) {
            copyAssetFile(asset, basedir + "/assets/" + asset);
        }
    }

    private void recursiveDelete(File file) {
        if (file.isDirectory()) {
            for (File f : file.listFiles())
                recursiveDelete(f);
        }
        Log.i("Mnemosyne", "Removing " + file.getAbsolutePath());
        file.delete();
    }

    private ProgressDialog progressDialog;
    @Override
    protected void onPreExecute() {
        long appLastUpdate = this.getAppLastUpdate();
        long assetLastModified = this.getAssetLastModified();
        if (appLastUpdate > assetLastModified) {
            progressDialog = new ProgressDialog(UIActivity);
            progressDialog.setCancelable(false);
            progressDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
            progressDialog.setMessage("Finalising Mnemosyne install. Please be patient...");
            progressDialog.setIndeterminate(true);
            progressDialog.show();
        }
    }

    @Override
    protected Void doInBackground (Void... params) {
        long appLastUpdate = this.getAppLastUpdate();
        long assetLastModified = this.getAssetLastModified();
        if (appLastUpdate <= assetLastModified) {
            Log.i("Mnemosyne", "Assets are up to date");
        } else {
            // Make sure to delete old starcore files.
            File destDir = new File(basedir + "/files");
            if (destDir.exists()) {
                recursiveDelete(destDir);
                Log.i("Mnemosyne", "Removed previous assets from " + destDir);
            }
            // Delete previous assets.
            destDir = new File(basedir + "/assets");
            if (destDir.exists()) {
                recursiveDelete(destDir);
                Log.i("Mnemosyne", "Removed previous assets from " + destDir);
            }
            Log.i("Mnemosyne", "About to extract assets");
            try {
                copyAssets("python");
            } catch (Exception e) {
                AlertDialog.Builder alert = new AlertDialog.Builder(UIActivity);
                alert.setMessage(e.toString());
                alert.setCancelable(false);
                alert.show();
                e.printStackTrace();
            }
            this.setAssetLastModified(appLastUpdate);
            Log.i("Mnemosyne", "Done extracting assets");
        }

        //String path = basedir + "/assets"; //
        //Log.d("Mnemosyne", "Listing files in path: " + path);
        //File f = new File(path);
        //File file[] = f.listFiles();
        //Log.d("Mnemosyne", "Number of files: " + file.length);
        //for (int i=0; i < file.length; i++) {
        //    Log.d("Mnemosyne", "FileName:" + file[i].getName());
        //}

        return null;
    }

    @Override
    protected void onPostExecute(Void result) {
        if (progressDialog != null) {
            progressDialog.dismiss();
        }
        UIActivity.continueOnCreate();
    }
}