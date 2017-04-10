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
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.BufferedWriter;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

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
        String filename = basedir + "/files/" + mAssetModifiedPath;
        try {
            BufferedWriter bwriter = new BufferedWriter(new FileWriter(new File(filename)));
            bwriter.write(String.format("%d", time));
            bwriter.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private long getAssetLastModified() {
        String filename = basedir + "/files/" + mAssetModifiedPath;
        try {
            BufferedReader breader = new BufferedReader(new FileReader(new File(filename)));
            String contents = breader.readLine();
            breader.close();
            return Long.valueOf(contents).longValue();
        } catch (IOException e) {
            e.printStackTrace();
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

    private void copyFile(String Name, String desPath) throws IOException {
        File outfile = new File(basedir + "/files/" + desPath + Name);
        if (!outfile.exists()) {
            outfile.createNewFile();
            FileOutputStream out = new FileOutputStream(outfile);
            byte[] buffer = new byte[1024];
            InputStream in;
            int readLen = 0;
            in = UIActivity.getAssets().open(desPath + Name);
            while ((readLen = in.read(buffer)) != -1){
                out.write(buffer, 0, readLen);
            }
            out.flush();
            in.close();
            out.close();
        }
    }

    private boolean CreatePath(String Path){
        File destCardDir = new File(Path);
        if (!destCardDir.exists()) {
            int index = Path.lastIndexOf(File.separator.charAt(0));
            if (index < 0) {
                if (destCardDir.mkdirs() == false)
                    return false;
            } else {
                String ParentPath = Path.substring(0, index);
                if (CreatePath(ParentPath) == false)
                    return false;
                if (destCardDir.mkdirs() == false)
                    return false;
            }
        }
        return true;
    }

    private boolean unzip(InputStream zipFileName, String outputDirectory, Boolean OverWriteFlag) {
        try {
            ZipInputStream in = new ZipInputStream(zipFileName);
            ZipEntry entry = in.getNextEntry();
            byte[] buffer = new byte[1024];
            File file = new File(outputDirectory);
            if (! file.exists()) {
                file.mkdir();
            }
            while (entry != null) {
                if (entry.isDirectory()) {
                    String name = entry.getName();
                    name = name.substring(0, name.length() - 1);
                    if (CreatePath(outputDirectory + File.separator + name) == false)
                        return false;
                } else {
                    String name = outputDirectory + File.separator + entry.getName();
                    int index = name.lastIndexOf(File.separator.charAt(0));
                    if (index < 0) {
                        file = new File(outputDirectory + File.separator + entry.getName());
                    } else {
                        String ParentPath = name.substring(0, index);
                        if (CreatePath(ParentPath) == false)
                            return false;
                        file = new File(outputDirectory + File.separator + entry.getName());
                    }
                    if (!file.exists() || OverWriteFlag == true) {
                        file.createNewFile();
                        FileOutputStream out = new FileOutputStream(file);
                        int readLen = 0;
                        while ((readLen = in.read(buffer)) != -1) {
                            out.write(buffer, 0, readLen);
                        }
                        out.close();
                    }
                }
                entry = in.getNextEntry();
            }
            in.close();
            return true;
        } catch (FileNotFoundException e) {
            e.printStackTrace();
            return false;
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }
    }

    void deleteRecursive(File fileOrDirectory) {
        if (fileOrDirectory.isDirectory())
            for (File child : fileOrDirectory.listFiles())
                deleteRecursive(child);
        fileOrDirectory.delete();
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
            Log.i("Mnemosyne", "Removing previous assets");
            File destDir = new File(basedir + "/files");
            if (destDir.exists()) {
                deleteRecursive(destDir);}

            Log.d("Mnemosyne", "About to extract Mnemosyne");
            try {
                destDir.mkdirs();
                InputStream dataSource = UIActivity.getAssets().open("python3.4.zip");
                boolean result = unzip(dataSource, basedir + "/files", true);
                if (! result) {
                    Log.i("Mnemosyne", "Could not unzip mnemosyne.zip.");
                    progressDialog.dismiss();
                    AlertDialog.Builder alert = new AlertDialog.Builder(UIActivity);
                    alert.setMessage("Could not unzip python3.4.zip");
                    alert.setCancelable(false);
                    alert.show();
                }

                java.io.File zlibFile = new java.io.File(basedir + "/files/zlib.cpython-34m.so");
                copyFile("zlib.cpython-34m.so", "");

                destDir = new File(basedir + "/files/lib-dynload");
                destDir.mkdirs();

                copyFile("_bisect.cpython-34m.so", "lib-dynload/");
                copyFile("_codecs_cn.cpython-34m.so", "lib-dynload/");
                copyFile("_codecs_hk.cpython-34m.so", "lib-dynload/");
                copyFile("_codecs_iso2022.cpython-34m.so", "lib-dynload/");
                copyFile("_codecs_jp.cpython-34m.so", "lib-dynload/");
                copyFile("_codecs_kr.cpython-34m.so", "lib-dynload/");
                copyFile("_codecs_tw.cpython-34m.so", "lib-dynload/");
                copyFile("_crypt.cpython-34m.so", "lib-dynload/");
                copyFile("_csv.cpython-34m.so", "lib-dynload/");
                copyFile("_ctypes.cpython-34m.so", "lib-dynload/");
                copyFile("_ctypes_test.cpython-34m.so", "lib-dynload/");
                copyFile("_datetime.cpython-34m.so", "lib-dynload/");
                copyFile("_elementtree.cpython-34m.so", "lib-dynload/");
                copyFile("_heapq.cpython-34m.so", "lib-dynload/");
                copyFile("_json.cpython-34m.so", "lib-dynload/");
                copyFile("_lsprof.cpython-34m.so", "lib-dynload/");
                copyFile("_md5.cpython-34m.so", "lib-dynload/");
                copyFile("_multibytecodec.cpython-34m.so", "lib-dynload/");
                copyFile("_multiprocessing.cpython-34m.so", "lib-dynload/");
                copyFile("_opcode.cpython-34m.so", "lib-dynload/");
                copyFile("_pickle.cpython-34m.so", "lib-dynload/");
                copyFile("_posixsubprocess.cpython-34m.so", "lib-dynload/");
                copyFile("_random.cpython-34m.so", "lib-dynload/");
                copyFile("_sha1.cpython-34m.so", "lib-dynload/");
                copyFile("_sha256.cpython-34m.so", "lib-dynload/");
                copyFile("_sha512.cpython-34m.so", "lib-dynload/");
                copyFile("_socket.cpython-34m.so", "lib-dynload/");
                copyFile("_sqlite3.cpython-34m.so", "lib-dynload/");
                copyFile("_struct.cpython-34m.so", "lib-dynload/");
                copyFile("_testbuffer.cpython-34m.so", "lib-dynload/");
                copyFile("_testcapi.cpython-34m.so", "lib-dynload/");
                copyFile("_testimportmultiple.cpython-34m.so", "lib-dynload/");
                copyFile("array.cpython-34m.so", "lib-dynload/");
                copyFile("audioop.cpython-34m.so", "lib-dynload/");
                copyFile("binascii.cpython-34m.so", "lib-dynload/");
                copyFile("cmath.cpython-34m.so", "lib-dynload/");
                copyFile("fcntl.cpython-34m.so", "lib-dynload/");
                copyFile("grp.cpython-34m.so", "lib-dynload/");
                copyFile("math.cpython-34m.so", "lib-dynload/");
                copyFile("mmap.cpython-34m.so", "lib-dynload/");
                copyFile("parser.cpython-34m.so", "lib-dynload/");
                copyFile("pyexpat.cpython-34m.so", "lib-dynload/");
                copyFile("resource.cpython-34m.so", "lib-dynload/");
                copyFile("select.cpython-34m.so", "lib-dynload/");
                copyFile("syslog.cpython-34m.so", "lib-dynload/");
                copyFile("termios.cpython-34m.so", "lib-dynload/");
                copyFile("time.cpython-34m.so", "lib-dynload/");
                copyFile("unicodedata.cpython-34m.so", "lib-dynload/");
                copyFile("xxlimited.cpython-34m.so", "lib-dynload/");
                copyFile("zlib.cpython-34m.so", "lib-dynload/");

                dataSource = UIActivity.getAssets().open("mnemosyne.zip");
                result = unzip(dataSource, basedir + "/files", true);
                if (! result) {
                    Log.i("Mnemosyne", "Could not unzip mnemosyne.zip.");
                    progressDialog.dismiss();
                    AlertDialog.Builder alert = new AlertDialog.Builder(UIActivity);
                    alert.setMessage("Could not unzip mnemosyne.zip.");
                    alert.setCancelable(false);
                    alert.show();
                }
            } catch (Exception e) {
                AlertDialog.Builder alert = new AlertDialog.Builder(UIActivity);
                alert.setMessage(e.toString());
                alert.setCancelable(false);
                alert.show();
                e.printStackTrace();
            }
            this.setAssetLastModified(appLastUpdate);
            Log.i("Mnemosyne", "Done extracting Mnemosyne");
        }

        //String path = basedir + "/files/lib-dynload";
        //Log.d("Mnemosyne", "Path: " + path);
        //File f = new File(path);
        //File file[] = f.listFiles();
        //Log.d("Mnemosyne", "Size: "+ file.length);
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