package org.mnemosyne;

import com.srplab.www.starcore.StarCoreFactory;
import com.srplab.www.starcore.StarCoreFactoryPath;
import com.srplab.www.starcore.StarObjectClass;
import com.srplab.www.starcore.StarServiceClass;
import com.srplab.www.starcore.StarSrvGroupClass;

import android.app.Activity;
import android.content.res.AssetManager;
import android.os.Bundle;
import android.webkit.WebView;
import android.widget.TextView;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

public class MnemosyneActivity extends Activity {

    static TextView questionLabel;
    static WebView question;
    static WebView answer;

    private void mergeApkFile(Activity c, ArrayList<String> partFileList, String dst)
            throws IOException {
        if (!new File(partFileList.get(0)).exists()) {
            //OutputStream out = new FileOutputStream(dst);
            OutputStream out = openFileOutput(dst, MODE_WORLD_READABLE );
            byte[] buffer = new byte[1024];
            InputStream in;
            int readLen = 0;
            for(int i = 0; i < partFileList.size(); i++){
                in = c.getAssets().open(partFileList.get(i));
                while ((readLen = in.read(buffer)) != -1) {
                    out.write(buffer, 0, readLen);
                }
                out.flush();
                in.close();
            }
            out.close();
        }
    }

    private void copyFile(Activity c, String Name,String desPath) throws IOException {
        File outfile = new File("/data/data/" + getPackageName() + "/files/" + desPath+Name);
        if (!outfile.exists()) {
            outfile.createNewFile();
            FileOutputStream out = new FileOutputStream(outfile);
            byte[] buffer = new byte[1024];
            InputStream in;
            int readLen = 0;
            in = c.getAssets().open(desPath + Name);
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
            int Index = Path.lastIndexOf(File.separator.charAt(0));
            if (Index < 0) {
                if( destCardDir.mkdirs() == false )
                    return false;
            } else {
                String ParentPath = Path.substring(0, Index);
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
                    int Index = name.lastIndexOf(File.separator.charAt(0));
                    if (Index < 0) {
                        file = new File(outputDirectory + File.separator + entry.getName());
                    } else {
                        String ParentPath = name.substring(0, Index);
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

    private void setupMnemosyne() {
        java.io.File python_extras_r14File = new java.io.File("/data/data/" + getPackageName() +
                "/files/python_extras_r14.zip");
        if (!python_extras_r14File.exists()) {
            ArrayList<String> StarCoreFiles =  new ArrayList<String>();
            StarCoreFiles.add("python_extras_r14_aa");
            StarCoreFiles.add("python_extras_r14_ab");
            StarCoreFiles.add("python_extras_r14_ac");
            StarCoreFiles.add("python_extras_r14_ad");
            try {
                mergeApkFile(this,StarCoreFiles,"python_extras_r14.zip");
            }
            catch (Exception e) {
                e.printStackTrace();
            }
        }

        File destDir = new File("/data/data/" + getPackageName() + "/files/lib-dynload");
        if (!destDir.exists())
            destDir.mkdirs();
        try {
            copyFile(this,"_bisect.so","lib-dynload/");
            copyFile(this,"_bytesio.so","lib-dynload/");
            copyFile(this,"_codecs_cn.so","lib-dynload/");
            copyFile(this,"_codecs_hk.so","lib-dynload/");
            copyFile(this,"_codecs_iso2022.so","lib-dynload/");
            copyFile(this,"_codecs_jp.so","lib-dynload/");
            copyFile(this,"_codecs_kr.so","lib-dynload/");
            copyFile(this,"_codecs_tw.so","lib-dynload/");
            copyFile(this,"_collections.so","lib-dynload/");
            copyFile(this,"_ctypes.so","lib-dynload/");
            copyFile(this,"_ctypes_test.so","lib-dynload/");
            copyFile(this,"_elementtree.so","lib-dynload/");
            copyFile(this,"_fileio.so","lib-dynload/");
            copyFile(this,"_functools.so","lib-dynload/");
            copyFile(this,"_heapq.so","lib-dynload/");
            copyFile(this,"_hotshot.so","lib-dynload/");
            copyFile(this,"_json.so","lib-dynload/");
            copyFile(this,"_lsprof.so","lib-dynload/");
            copyFile(this,"_md5.so","lib-dynload/");
            copyFile(this,"_multibytecodec.so","lib-dynload/");
            copyFile(this,"_multiprocessing.so","lib-dynload/");
            copyFile(this,"_random.so","lib-dynload/");
            copyFile(this,"_sha256.so","lib-dynload/");
            copyFile(this,"_sha512.so","lib-dynload/");
            copyFile(this,"_sha.so","lib-dynload/");
            copyFile(this,"_socket.so","lib-dynload/");
            copyFile(this,"_sqlite3.so","lib-dynload/");
            copyFile(this,"_ssl.so","lib-dynload/");
            copyFile(this,"_struct.so","lib-dynload/");
            copyFile(this,"_testcapi.so","lib-dynload/");
            copyFile(this,"_weakref.so","lib-dynload/");
            copyFile(this,"array.so","lib-dynload/");
            copyFile(this,"audioop.so","lib-dynload/");
            copyFile(this,"binascii.so","lib-dynload/");
            copyFile(this,"bz2.so","lib-dynload/");
            copyFile(this,"cmath.so","lib-dynload/");
            copyFile(this,"cPickle.so","lib-dynload/");
            copyFile(this,"crypt.so","lib-dynload/");
            copyFile(this,"cStringIO.so","lib-dynload/");
            copyFile(this,"datetime.so","lib-dynload/");
            copyFile(this,"fcntl.so","lib-dynload/");
            copyFile(this,"future_builtins.so","lib-dynload/");
            copyFile(this,"imageop.so","lib-dynload/");
            copyFile(this,"itertools.so","lib-dynload/");
            copyFile(this,"math.so","lib-dynload/");
            copyFile(this,"mmap.so","lib-dynload/");
            copyFile(this,"operator.so","lib-dynload/");
            copyFile(this,"parser.so","lib-dynload/");
            copyFile(this,"pyexpat.so","lib-dynload/");
            copyFile(this,"resource.so","lib-dynload/");
            copyFile(this,"select.so","lib-dynload/");
            copyFile(this,"strop.so","lib-dynload/");
            copyFile(this,"syslog.so","lib-dynload/");
            copyFile(this,"termios.so","lib-dynload/");
            copyFile(this,"time.so","lib-dynload/");
            copyFile(this,"unicodedata.so","lib-dynload/");
            copyFile(this,"zlib.so","lib-dynload/");
        }
        catch (Exception e) {
            e.printStackTrace();
        }

        try {
            AssetManager assetManager = getAssets();
            InputStream dataSource = assetManager.open("mnemosyne.zip");
            StarCoreFactoryPath.CreatePath(Runtime.getRuntime(),
                    "/data/data/" + getPackageName() + "/files");
            unzip(dataSource, "/data/data/" + getPackageName() + "/files", true);
        }
        catch (IOException e) {
            e.printStackTrace();
        }

        StarCoreFactoryPath.StarCoreCoreLibraryPath = "/data/data/" + getPackageName() + "/lib";
        StarCoreFactoryPath.StarCoreShareLibraryPath = "/data/data/" + getPackageName() + "/lib";
        StarCoreFactoryPath.StarCoreOperationPath = "/data/data/" + getPackageName() + "/files";
        StarCoreFactory starcore = StarCoreFactory.GetFactory();

        StarSrvGroupClass SrvGroup = starcore._GetSrvGroup(0);
        StarServiceClass Service = SrvGroup._GetService("test", "123");
        StarObjectClass python = null;
        if (Service == null) {  // The service has not been initialized.
            Service = starcore._InitSimple("test", "123", 0, 0);
            Service._CheckPassword(false);
            SrvGroup = (StarSrvGroupClass) Service._Get("_ServiceGroup");
            SrvGroup._InitRaw("python", Service);
            python = Service._ImportRawContext("python", "", false, "");

            // Set up extra paths.
            python._Call("import", "sys");
            StarObjectClass pythonSys = python._GetObject("sys");
            StarObjectClass pythonPath = (StarObjectClass) pythonSys._Get("path");
            String base = "/data/data/" + getPackageName();
            pythonPath._Call("insert", 0, base + "/files/python_extras_r14.zip");
            pythonPath._Call("insert", 0, base + "/lib");
            pythonPath._Call("insert", 0, base + "/files/lib-dynload");
            pythonPath._Call("insert", 0, base + "/files");

            // Start Mnemosyne.
            SrvGroup._LoadRawModule("python", "", "/data/data/" + getPackageName() +
                    "/files/mnemosyne/cle/mnemosyne_android.py", false);
            //SrvGroup._LoadRawModule("python", "", "/data/data/" + getPackageName() +
            //        "/files/mnemosyne/cle/callback.py", false);
            StarObjectClass mnemosyne = python._GetObject("mnemosyne");


            String dataDir = "/sdcard/Mnemosyne/";
            String filename = "default.db";
            StarObjectClass activity = Service._New();
            activity._AttachRawObject(this, false);

            python._Call("start_mnemosyne", dataDir, filename, activity);
        }
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        setupMnemosyne();

        questionLabel = (TextView) this.findViewById(R.id.questionLabel);
        question = (WebView) this.findViewById(R.id.question);
        answer = (WebView) this.findViewById(R.id.answer);
    }

    public void setQuestionLabel(String label) {
        questionLabel.setText(label);
    }

    public void setQuestion(String html) {
        question.loadDataWithBaseURL(null, html, "text/html", "utf-8", null);
    }

    public void setAnswer(String html) {
        answer.loadDataWithBaseURL(null, html, "text/html", "utf-8", null);
    }
}