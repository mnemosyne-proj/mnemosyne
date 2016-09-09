package org.mnemosyne;

import com.srplab.www.starcore.StarCoreFactoryPath;

import android.app.ProgressDialog;
import android.os.AsyncTask;
import android.os.Handler;
import android.util.Log;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

public class MnemosyneInstaller extends AsyncTask<Void, Void, Void>  {

    private MnemosyneActivity UIActivity;
    private String basedir;
    Handler UIHandler;

    public MnemosyneInstaller(MnemosyneActivity activity, Handler handler)
    {
        UIActivity = activity;
        UIHandler = handler;
        basedir = "/data/data/" + UIActivity.getPackageName();
    }

    private void mergeApkFile(ArrayList<String> partFileList, String dst)
            throws IOException {
        if (!new File(partFileList.get(0)).exists()) {
            OutputStream out = UIActivity.openFileOutput(dst, UIActivity.MODE_WORLD_READABLE);
            byte[] buffer = new byte[1024];
            InputStream in;
            int readLen = 0;
            for (int i=0; i<partFileList.size(); i++){
                in = UIActivity.getAssets().open(partFileList.get(i));
                while ((readLen = in.read(buffer)) != -1) {
                    out.write(buffer, 0, readLen);
                }
                out.flush();
                in.close();
            }
            out.close();
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
            while (entry != null) {
                File file = new File(outputDirectory);
                file.mkdir();
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

    private ProgressDialog progressDialog;
    @Override
    protected void onPreExecute() {
        progressDialog = new ProgressDialog(UIActivity);

        progressDialog.setCancelable(false);
        progressDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
        progressDialog.setMessage("Preparing to run Mnemosyne...");
        progressDialog.setIndeterminate(true);
        progressDialog.show();
    }

    @Override
    protected Void doInBackground (Void... params) {
        Log.d("Mnemosyne", "About to extract Mnemosyne");

        File destDir = new File(basedir + "/files");

        // TODO: do this on first starting new version
        //deleteRecursive(destDir);

        if( !destDir.exists() )
            destDir.mkdirs();
        java.io.File pythonlibFile = new java.io.File(basedir +"/files/python3.4.zip");
        if( !pythonlibFile.exists() ){
            try{
                copyFile("python3.4.zip", "");
            }
            catch(Exception e){
                e.printStackTrace();
            }
        }
        java.io.File zlibFile = new java.io.File(basedir + "/files/zlib.cpython-34m.so");
        if( !zlibFile.exists() ){
            try{
                copyFile("zlib.cpython-34m.so", "");
            }
            catch(Exception e){
                e.printStackTrace();
            }
        }

        destDir = new File(basedir + "/files/lib-dynload");
        if (!destDir.exists())
            destDir.mkdirs();
        try {
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
        }
        catch (Exception e) {
            e.printStackTrace();
        }

        try {
            InputStream dataSource = UIActivity.getAssets().open("mnemosyne.zip");
            StarCoreFactoryPath.CreatePath(Runtime.getRuntime(), basedir + "/files");
            unzip(dataSource, basedir + "/files", true);
        }
        catch (IOException e) {
            e.printStackTrace();
        }

        Log.d("Mnemosyne", "Extracted Mnemosyne");

        String path = basedir + "/files/lib-dynload";
        Log.d("Mnemosyne", "Path: " + path);
        File f = new File(path);
        File file[] = f.listFiles();
        Log.d("Mnemosyne", "Size: "+ file.length);
        for (int i=0; i < file.length; i++)
        {
            Log.d("Mnemosyne", "FileName:" + file[i].getName());
        }


        return null;
    }

    void deleteRecursive(File fileOrDirectory) {
        if (fileOrDirectory.isDirectory())
            for (File child : fileOrDirectory.listFiles())
                deleteRecursive(child);

        fileOrDirectory.delete();
    }

    @Override
    protected void onPostExecute(Void result) {
        progressDialog.dismiss();
        UIActivity.continueOnCreate();
    }

}
