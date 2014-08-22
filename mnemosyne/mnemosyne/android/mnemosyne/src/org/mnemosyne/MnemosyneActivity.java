package org.mnemosyne;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.ProgressDialog;
import android.content.DialogInterface;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
import android.webkit.WebView;
import android.widget.Button;
import android.widget.TextView;

public class MnemosyneActivity extends Activity {

    Handler activityHandler = new Handler();
    MnemosyneThread mnemosyneThread;

    TextView questionLabel;
    TextView answerLabel;
    TextView statusbar;
    WebView question;
    WebView answer;
    Button showAnswerButton;
    Button button0;
    Button button1;
    Button button2;
    Button button3;
    Button button4;
    Button button5;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);

        questionLabel = (TextView) this.findViewById(R.id.questionLabel);
        question = (WebView) this.findViewById(R.id.question);
        answerLabel = (TextView) this.findViewById(R.id.answerLabel);
        answer = (WebView) this.findViewById(R.id.answer);
        showAnswerButton = (Button) this.findViewById(R.id.showAnswerButton);
        button0 = (Button) this.findViewById(R.id.button0);
        button1 = (Button) this.findViewById(R.id.button1);
        button2 = (Button) this.findViewById(R.id.button2);
        button3 = (Button) this.findViewById(R.id.button3);
        button4 = (Button) this.findViewById(R.id.button4);
        button5 = (Button) this.findViewById(R.id.button5);
        statusbar = (TextView) this.findViewById(R.id.statusbar);

        MnemosyneInstaller installer = new MnemosyneInstaller(this);
        installer.installMnemosyne();

        mnemosyneThread = new MnemosyneThread(this, activityHandler, getPackageName());
        mnemosyneThread.start();

        //testProgress();

        showAnswerButton.setOnClickListener(new OnClickListener() {
            public void onClick(View view) {
                mnemosyneThread.getHandler().post(new Runnable() {
                    public void run() {
                        mnemosyneThread.reviewController._Call("show_answer");
                    }
                });
            }
        });

        button0.setOnClickListener(new OnClickListener() {
            public void onClick(View view) {
                mnemosyneThread.getHandler().post(new Runnable() {
                    public void run() {
                        mnemosyneThread.reviewController._Call("grade_answer", 0);
                    }
                });
            }
        });

        button1.setOnClickListener(new OnClickListener() {
            public void onClick(View view) {
                mnemosyneThread.getHandler().post(new Runnable() {
                    public void run() {
                        mnemosyneThread.reviewController._Call("grade_answer", 1);
                    }
                });
            }
        });

        button2.setOnClickListener(new OnClickListener() {
            public void onClick(View view) {
                mnemosyneThread.getHandler().post(new Runnable() {
                    public void run() {
                        mnemosyneThread.reviewController._Call("grade_answer", 2);
                    }
                });
            }
        });

        button3.setOnClickListener(new OnClickListener() {
            public void onClick(View view) {
                mnemosyneThread.getHandler().post(new Runnable() {
                    public void run() {
                        mnemosyneThread.reviewController._Call("grade_answer", 3);
                    }
                });
            }
        });

        button4.setOnClickListener(new OnClickListener() {
            public void onClick(View view) {
                mnemosyneThread.getHandler().post(new Runnable() {
                    public void run() {
                        mnemosyneThread.reviewController._Call("grade_answer", 4);
                    }
                });
            }
        });

        button5.setOnClickListener(new OnClickListener() {
            public void onClick(View view) {
                mnemosyneThread.getHandler().post(new Runnable() {
                    public void run() {
                        mnemosyneThread.reviewController._Call("grade_answer", 5);
                    }
                });
            }
        });

    }

    public void showInformation(String text) {
        AlertDialog.Builder alert = new AlertDialog.Builder(this);
        alert.setMessage(text);
        alert.setCancelable(false);
        alert.setPositiveButton("OK", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int whichButton) {
                return;
            }
        });
        alert.show();
    }

    private int result = -1;

    public int showQuestion(String text, String option0, String option1, String option2) {

        // Make a handler that throws a runtime exception when a message is received.
        final Handler _handler = new Handler() {
            @Override
            public void handleMessage(Message mesg) {
                throw new RuntimeException();
            }
        };

        AlertDialog.Builder alert = new AlertDialog.Builder(this);
        alert.setMessage(text);
        alert.setCancelable(false);
        alert.setPositiveButton(option0, new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int whichButton) {
                result = 0;
                _handler.sendMessage(_handler.obtainMessage());
            }
        });
        alert.setNeutralButton(option1, new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int whichButton) {
                result = 1;
                _handler.sendMessage(_handler.obtainMessage());
            }
        });
        alert.setNegativeButton(option2, new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int whichButton) {
                result = 2;
                _handler.sendMessage(_handler.obtainMessage());
            }

        });

        alert.show();
        // Loop until the user selects an answer and a runtime exception is triggered.
        try {
            Looper.loop();
        }
        catch (RuntimeException exception) {
        }
        return result;
    }

    private ProgressDialog progressDialog;

    private int progressValue = 0;

    public void setProgressText(String text) {
        progressDialog = new ProgressDialog(this);
        progressDialog.setCancelable(false);
        progressDialog.setProgressStyle(ProgressDialog.STYLE_HORIZONTAL);
        progressDialog.setMessage(text);
        progressDialog.setProgress(0);
        progressDialog.show();
        Log.d("Mnemosyne", "done set progress text ");
    }

    public void setProgressRange(int maximum) {
        progressDialog.setMax(maximum);
    }

    public void setProgressValue(int value) {
        Log.d("Mnemosyne", "setProgressValue " + value);
        if (value >= progressDialog.getMax()) {
            closeProgress();
            return;
        }
        progressValue = value;
        //progressDialog.setProgress(progressValue);

        // handler.post(new Runnable() {
        //    public void run() {
        //         progressDialog.setProgress(progressValue);
        //         Log.d("Mnemosyne", "handler " + progressValue);
        //     }
        // });
    }

    public void closeProgress() {
        progressDialog.dismiss();
    }

    public void testProgress() {
        Log.d("Mnemosyne", "testProgress ");

        //handler.post(new Runnable() {
        //    public void run() {
        //        Log.d("Mnemosyne", "runnable creating ui");
        //        setProgressText("progress2");
        //        setProgressRange(3);
        //    }
        //});

        Thread t = new Thread(new Runnable() {
            public void run() {
                for (int i=1; i<4; i++) {
                    Log.d("Mnemosyne", "in thread " + i);
                    // your computer is too fast, sleep 1 second
                    try {
                        Thread.sleep(1000);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    Log.d("Mnemosyne", "A " + i);
                    //mainWidget._Call("set_progress_value", i);
                    setProgressValue(i);
                    Log.d("Mnemosyne", "B " + i);
                }
            }
        });

    }
}