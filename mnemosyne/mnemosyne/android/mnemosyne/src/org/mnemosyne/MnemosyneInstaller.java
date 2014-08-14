package org.mnemosyne;

import com.srplab.www.starcore.StarCoreFactoryPath;

import android.app.Activity;
import android.content.res.AssetManager;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

public class MnemosyneInstaller {

    private AssetManager assetManager;
    private String basedir;

    public MnemosyneInstaller(Activity activity, String packageName)
    {
        assetManager = activity.getAssets();
        basedir = "/data/data/" + packageName;
    }

    private void mergeApkFile(ArrayList<String> partFileList, String dst)
            throws IOException {
        if (!new File(partFileList.get(0)).exists()) {
            OutputStream out = new FileOutputStream(dst);
            //OutputStream out = openFileOutput(dst, MODE_WORLD_READABLE);
            byte[] buffer = new byte[1024];
            InputStream in;
            int readLen = 0;
            for(int i = 0; i < partFileList.size(); i++){
                in = assetManager.open(partFileList.get(i));
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
        File outfile = new File(basedir + "/files/" + desPath+Name);
        if (!outfile.exists()) {
            outfile.createNewFile();
            FileOutputStream out = new FileOutputStream(outfile);
            byte[] buffer = new byte[1024];
            InputStream in;
            int readLen = 0;
            in = assetManager.open(desPath + Name);
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

    public void installMnemosyne() {
        java.io.File python_extras_r14File = new java.io.File(basedir +
                "/files/python_extras_r14.zip");
        if (!python_extras_r14File.exists()) {
            ArrayList<String> StarCoreFiles =  new ArrayList<String>();
            StarCoreFiles.add("python_extras_r14_aa");
            StarCoreFiles.add("python_extras_r14_ab");
            StarCoreFiles.add("python_extras_r14_ac");
            StarCoreFiles.add("python_extras_r14_ad");
            try {
                mergeApkFile(StarCoreFiles, "python_extras_r14.zip");
            }
            catch (Exception e) {
                e.printStackTrace();
            }
        }

        File destDir = new File(basedir + "/files/lib-dynload");
        if (! destDir.exists())
            destDir.mkdirs();
        try {
            copyFile("_bisect.so", "lib-dynload/");
            copyFile("_bytesio.so", "lib-dynload/");
            copyFile("_codecs_cn.so", "lib-dynload/");
            copyFile("_codecs_hk.so", "lib-dynload/");
            copyFile("_codecs_iso2022.so", "lib-dynload/");
            copyFile("_codecs_jp.so", "lib-dynload/");
            copyFile("_codecs_kr.so", "lib-dynload/");
            copyFile("_codecs_tw.so", "lib-dynload/");
            copyFile("_collections.so", "lib-dynload/");
            copyFile("_ctypes.so", "lib-dynload/");
            copyFile("_ctypes_test.so", "lib-dynload/");
            copyFile("_elementtree.so", "lib-dynload/");
            copyFile("_fileio.so", "lib-dynload/");
            copyFile("_functools.so", "lib-dynload/");
            copyFile("_heapq.so", "lib-dynload/");
            copyFile("_hotshot.so", "lib-dynload/");
            copyFile("_json.so", "lib-dynload/");
            copyFile("_lsprof.so", "lib-dynload/");
            copyFile("_md5.so", "lib-dynload/");
            copyFile("_multibytecodec.so", "lib-dynload/");
            copyFile("_multiprocessing.so", "lib-dynload/");
            copyFile("_random.so", "lib-dynload/");
            copyFile("_sha256.so", "lib-dynload/");
            copyFile("_sha512.so", "lib-dynload/");
            copyFile("_sha.so", "lib-dynload/");
            copyFile("_socket.so", "lib-dynload/");
            copyFile("_sqlite3.so", "lib-dynload/");
            copyFile("_ssl.so", "lib-dynload/");
            copyFile("_struct.so", "lib-dynload/");
            copyFile("_testcapi.so", "lib-dynload/");
            copyFile("_weakref.so", "lib-dynload/");
            copyFile("array.so", "lib-dynload/");
            copyFile("audioop.so", "lib-dynload/");
            copyFile("binascii.so", "lib-dynload/");
            copyFile("bz2.so", "lib-dynload/");
            copyFile("cmath.so", "lib-dynload/");
            copyFile("cPickle.so", "lib-dynload/");
            copyFile("crypt.so", "lib-dynload/");
            copyFile("cStringIO.so", "lib-dynload/");
            copyFile("datetime.so", "lib-dynload/");
            copyFile("fcntl.so", "lib-dynload/");
            copyFile("future_builtins.so", "lib-dynload/");
            copyFile("imageop.so", "lib-dynload/");
            copyFile("itertools.so", "lib-dynload/");
            copyFile("math.so", "lib-dynload/");
            copyFile("mmap.so", "lib-dynload/");
            copyFile("operator.so", "lib-dynload/");
            copyFile("parser.so", "lib-dynload/");
            copyFile("pyexpat.so", "lib-dynload/");
            copyFile("resource.so", "lib-dynload/");
            copyFile("select.so", "lib-dynload/");
            copyFile("strop.so", "lib-dynload/");
            copyFile("syslog.so", "lib-dynload/");
            copyFile("termios.so", "lib-dynload/");
            copyFile("time.so", "lib-dynload/");
            copyFile("unicodedata.so", "lib-dynload/");
            copyFile("zlib.so", "lib-dynload/");
        }
        catch (Exception e) {
            e.printStackTrace();
        }

        try {
            InputStream dataSource = assetManager.open("mnemosyne.zip");
            StarCoreFactoryPath.CreatePath(Runtime.getRuntime(), basedir + "/files");
            unzip(dataSource, basedir + "/files", true);
        }
        catch (IOException e) {
            e.printStackTrace();
        }
    }
}
