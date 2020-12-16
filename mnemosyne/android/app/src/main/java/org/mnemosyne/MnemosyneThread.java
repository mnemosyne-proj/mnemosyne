package org.mnemosyne;

import android.app.AlertDialog;
import android.app.ProgressDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import androidx.core.content.ContextCompat;
import android.util.Log;
import android.view.View;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;


public class MnemosyneThread extends Thread {

    MnemosyneActivity UIActivity;
    Handler mnemosyneHandler;
    Handler UIHandler;
    String basedir;
    ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
    MnemosyneBridge bridge;

    public MnemosyneThread(MnemosyneActivity activity, Handler handler, String packageName) {
        UIActivity = activity;
        UIHandler = handler;
        basedir = UIActivity.getApplicationInfo().dataDir;
        bridge = new MnemosyneBridge(basedir, activity, this);
    }

    public Handler getHandler() {
        return mnemosyneHandler;
    }

    public void startMnemosyne() {

        UIHandler.post(new Runnable() {
            public void run() {
                progressDialog = new ProgressDialog(UIActivity);
                progressDialog.setCancelable(false);
                progressDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
                progressDialog.setMessage("Initialising Mnemosyne...");
                progressDialog.setIndeterminate(true);
                progressDialog.show();
            }
        });

        // Determine datadir.
        String dataDir;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            dataDir = UIActivity.getFilesDir().getAbsolutePath();
        }
        else {
            // A user can set a datadir directory by putting a file 'datadir.txt' with
            // the directory in the default datadir.
            // This file contains e.g. "/storage/3738-3234/Android/data/org.mnemosyne/files"
            // in order to use a true external SD card. Note that /Android/... part is
            // important, otherwise we don't get access.

            dataDir = Environment.getExternalStorageDirectory().getPath() + "/Mnemosyne/";

            // Strangely enough we need this call first in order to be able to write
            // to the external directories.
            String dirList = "";
            for (File f : ContextCompat.getExternalFilesDirs(UIActivity, null)) {
                if (f != null) {  // Permission failure on some devices.
                    dirList += f.getPath() + "\n\n";
                }
            }

            try {
                InputStream is = new FileInputStream(dataDir + "/datadir.txt");
                BufferedReader buf = new BufferedReader(new InputStreamReader(is));
                String line = buf.readLine();
                if (!line.isEmpty()) {
                    dataDir = line;
                }
            } catch (FileNotFoundException e) {
                Log.i("Mnemosyne", "Redirection file not found:" + e.toString());
            } catch (IOException e) {
                Log.i("Mnemosyne", "Redirection file could not be read:" + e.toString());
            }

            File file = new File(dataDir);
            if (!file.exists()) {
                Boolean result = file.mkdirs();
                if (result == false) {
                    showInformation("Could not create data dir at " + dataDir + "\n" +
                            "Use a directory like:\n\n" + dirList);
                }
            } else {
                try {
                    File tmp = new File(dataDir + "/test.txt");
                    if (tmp.exists()) {
                        tmp.delete();
                    }
                    BufferedWriter bwriter = new BufferedWriter(new FileWriter(new File(dataDir + "/test.txt")));
                    bwriter.write("123");
                    bwriter.close();
                } catch (IOException e) {
                    e.printStackTrace();
                    showInformation("Could not create file in " + dataDir + "\nMake sure to give Mnemosyne write permission.");
                }
            }
        }
        Log.i("Mnemosyne", "datadir " + dataDir);

        File file2 = new File(dataDir + "/.nomedia");
        if (!file2.exists()){
            try {
                file2.createNewFile();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        bridge.startMnemosyne(dataDir, "default.db");

        // Set buttons correctly with respect to previous study mode.
        String studyModeId = bridge.config_get("study_mode");
        setGradeNames(studyModeId);
        setGradesEnabled(false);

        UIHandler.post(new Runnable() {
            public void run() {
                progressDialog.dismiss();
                UIActivity.setFullscreen();
            }
        });

        // Heartbeat: run at startup and then every 60 seconds.
        this.scheduler.scheduleAtFixedRate(new Runnable() {
            public void run() {
                mnemosyneHandler.post(new Runnable() {
                    public void run() {bridge.controller_heartbeat();
                    }
                });
            }
        }, 0, 60, TimeUnit.SECONDS);
    }

    public void pauseMnemosyne() {
        bridge.pauseMnemosyne();
    }

    public void stopMnemosyne() {
        bridge.stopMnemosyne();
        this.scheduler.shutdownNow();
    }

    @Override
    public void run() {
        Log.i("Mnemosyne", "About to run Mnemosyne thread");
        startMnemosyne();
        Looper.prepare();
        mnemosyneHandler = new Handler();
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

    public void setQuestion(String html) {
        final String _html = html;
        Log.i("Mnemosyne", "Question" + html);
        UIHandler.post(new Runnable() {
            public void run() {
                UIActivity.setQuestion(_html);
            }
        });
    }

    public void setAnswer(String html, boolean processAudio) {
        final String _html = html;
        final boolean _processAudio = processAudio;
        UIHandler.post(new Runnable() {
            public void run() {
                UIActivity.setAnswer(_html, _processAudio);
            }
        });
    }

    public void setQuestionBoxVisible(boolean isVisible) {
        final boolean _isVisible = isVisible;
        UIHandler.post(new Runnable() {
            public void run() {
                if (_isVisible) {
                    UIActivity.question.setVisibility(android.view.View.VISIBLE);
                    UIActivity.questionLabel.setVisibility(android.view.View.VISIBLE);
                }
                else {
                    UIActivity.question.setVisibility(android.view.View.GONE);
                    UIActivity.questionLabel.setVisibility(android.view.View.GONE);
                }
            }
        });
    }

    public void setAnswerBoxVisible(boolean isVisible) {
        final boolean _isVisible = isVisible;
        UIHandler.post(new Runnable() {
            public void run() {
                if (_isVisible) {
                    UIActivity.answer.setVisibility(android.view.View.VISIBLE);
                    UIActivity.answerLabel.setVisibility(android.view.View.VISIBLE);
                }
                else {
                    UIActivity.answer.setVisibility(android.view.View.GONE);
                    UIActivity.answerLabel.setVisibility(android.view.View.GONE);
                }
            }
        });
    }

    public void updateShowButton(String text, boolean isDefault, boolean isEnabled) {
        // We completely ignore isEnabled here, and rather chose to set it in
        // 'setGradesEnabled'. The reason is that breaking this up into two 'setVisibility'
        // messages causes screen flicker, probably related to ordering with respect to a
        // system-issued 'layout' call.
        // See http://stackoverflow.com/questions/3544826/android-home-screen-like-effect-flickering-problem-when-set-child-setvisibility
        final String _text = text;
        UIHandler.post(new Runnable() {
            public void run() {
                UIActivity.showAnswerButton.setText(_text);
            }
        });
    }

    public void setGradesEnabled(boolean isEnabled) {
        final boolean _isEnabled = isEnabled;
        final String studyModeId = bridge.config_get("study_mode");
        UIHandler.post(new Runnable() {
            public void run() {
                if (_isEnabled) {
                    UIActivity.button0.setVisibility(android.view.View.VISIBLE);
                    if (studyModeId.equals("ScheduledForgottenNew") || studyModeId.equals("NewOnly")) {
                            UIActivity.button1.setVisibility(android.view.View.VISIBLE);
                            UIActivity.button2.setVisibility(android.view.View.VISIBLE);
                            UIActivity.button3.setVisibility(android.view.View.VISIBLE);
                            UIActivity.button4.setVisibility(android.view.View.VISIBLE);
                        }
                    UIActivity.button5.setVisibility(android.view.View.VISIBLE);
                    UIActivity.showAnswerButton.setVisibility(android.view.View.GONE);
                }
                else {
                    UIActivity.button0.setVisibility(android.view.View.GONE);
                    UIActivity.button1.setVisibility(android.view.View.GONE);
                    UIActivity.button2.setVisibility(android.view.View.GONE);
                    UIActivity.button3.setVisibility(android.view.View.GONE);
                    UIActivity.button4.setVisibility(android.view.View.GONE);
                    UIActivity.button5.setVisibility(android.view.View.GONE);
                    UIActivity.showAnswerButton.setVisibility(android.view.View.VISIBLE);
                }
            }
        });
    }

    public void setGradeNames(String studyModeId)  {
        final String _studyModeId = studyModeId;
        UIHandler.post(new Runnable() {
            public void run() {
                if (_studyModeId.equals("CramAll") || _studyModeId.equals("CramRecent")) {
                    UIActivity.button0.setText("Wrong");
                    UIActivity.button1.setVisibility(android.view.View.GONE);
                    UIActivity.button2.setVisibility(android.view.View.GONE);
                    UIActivity.button3.setVisibility(android.view.View.GONE);
                    UIActivity.button4.setVisibility(android.view.View.GONE);
                    UIActivity.button5.setText("Right");
                }
                else {
                    UIActivity.button0.setText("0");
                    UIActivity.button1.setVisibility(android.view.View.VISIBLE);
                    UIActivity.button2.setVisibility(android.view.View.VISIBLE);
                    UIActivity.button3.setVisibility(android.view.View.VISIBLE);
                    UIActivity.button4.setVisibility(android.view.View.VISIBLE);
                    UIActivity.button5.setText("5");
                }
            }
        });
    }

    public void setStatusBarMessage(String text) {
        final String _text = text;
        UIHandler.post(new Runnable() {
            public void run() {
                UIActivity.statusbar.setText(_text);
            }
        });
    }

    public void showInformation(String text) {
        final String _text = text;
        UIHandler.post(new Runnable() {
            public void run() {
                AlertDialog.Builder alert = new AlertDialog.Builder(UIActivity);
                alert.setMessage(_text);
                alert.setCancelable(false);
                alert.setPositiveButton("OK", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int whichButton) {
                        return;
                    }
                });
                alert.show();
            }
        });
    }

    int result = -1;
    Semaphore semaphore = new Semaphore(0);

    public int showQuestion(String text, String option0, String option1, String option2) {
        final String _text = text;
        final String _option0 = option0;
        final String _option1 = option1;
        final String _option2 = option2;

        UIHandler.post(new Runnable() {
            public void run() {
                AlertDialog.Builder alert = new AlertDialog.Builder(UIActivity);
                alert.setMessage(_text);
                alert.setCancelable(false);
                alert.setPositiveButton(_option0, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int whichButton) {
                        result = 0;
                        semaphore.release();
                    }
                });
                alert.setNegativeButton(_option1, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int whichButton) {
                        result = 1;
                        semaphore.release();
                    }
                });
                alert.setNeutralButton(_option2, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int whichButton) {
                        result = 2;
                        semaphore.release();
                    }
                });

                //(AlertDialog)alert.getButton(DialogInterface.BUTTON_NEUTRAL).setMaxLines(2);

                alert.show();
            }
        });

        try {
            semaphore.acquire();
        }
        catch (InterruptedException e) {
        }
        return result;
    }

    public void syncDlgActivate() {
        final String server = bridge.config_get("server_for_sync_as_client");
        final String port = bridge.config_get("port_for_sync_as_client");
        final String username = bridge.config_get("username_for_sync_as_client");
        final String password = bridge.config_get("password_for_sync_as_client");

        UIHandler.post(new Runnable() {
            public void run() {
                Intent startSyncActivity = new Intent(UIActivity, SyncActivity.class);
                startSyncActivity.putExtra("server", server);
                startSyncActivity.putExtra("port", port);
                startSyncActivity.putExtra("username", username);
                startSyncActivity.putExtra("password", password);
                UIActivity.startActivityForResult(startSyncActivity, UIActivity.SYNC_ACTIVITY_RESULT);
            }
        });
    }

    public void activateCardsDlgActivate(String savedSets, String activeSet) {
        final String[] _savedSets = savedSets.split("____");
        if (_savedSets.length == 1 && _savedSets[0].equals("")) {
            showInformation("You don't have any saved sets defined. Please do so in the desktop app.");
            return;
        }

        final String _activeSet = activeSet;

        UIHandler.post(new Runnable() {
            public void run() {
                Intent activateActivity = new Intent(UIActivity, ActivateCardsActivity.class);
                Bundle bundle = new Bundle();
                bundle.putStringArray("saved_sets", _savedSets);
                bundle.putString("active_set", _activeSet);
                activateActivity.putExtras(bundle);
                UIActivity.startActivityForResult(activateActivity, UIActivity.ACTIVATE_CARDS_ACTIVITY_RESULT);
            }
        });
    }

    private ProgressDialog progressDialog;
    private int progressValue = 0;
    private String progressText = "";

    public void setProgressText(String text) {
        progressText = text;
        final String _text = text;
        UIHandler.post(new Runnable() {
            public void run() {
                if (progressDialog != null) {
                    progressDialog.dismiss();
                }
                progressDialog = new ProgressDialog(UIActivity);
                progressDialog.setCancelable(false);
                progressDialog.setMessage(_text);
                progressDialog.setProgress(0);
                progressValue = 0;
                progressDialog.show();
            }
        });
    }

    public void setProgressRange(int maximum) {
        final int _maximum = maximum;
        UIHandler.post(new Runnable() {
            public void run() {
                // Android doesn't like changing style on the fly, so we recreate the
                // progress dialog.
                if (progressDialog != null) {
                    progressDialog.dismiss();
                }
                progressDialog = new ProgressDialog(UIActivity);
                progressDialog.setCancelable(false);
                progressDialog.setMessage(progressText);
                progressDialog.setProgress(0);
                progressValue = 0;
                progressDialog.setProgressStyle(ProgressDialog.STYLE_HORIZONTAL);
                progressDialog.setMax(_maximum);
                progressDialog.show();
            }
        });
    }

    public void setProgressValue(int value) {
        final int _value = value;
        UIHandler.post(new Runnable() {
            public void run() {
                if (_value >= progressDialog.getMax()) {
                    closeProgress();
                    return;
                }
                progressValue = _value;
                progressDialog.setProgress(progressValue);
            }
        });
    }

    public void closeProgress() {
        UIHandler.post(new Runnable() {
            public void run() {
                if (progressDialog != null) {
                    progressDialog.dismiss();
                }
            }
        });
    }

}