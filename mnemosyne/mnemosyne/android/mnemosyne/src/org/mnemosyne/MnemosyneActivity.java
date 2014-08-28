package org.mnemosyne;

import android.app.Activity;
import android.content.res.Configuration;
import android.os.Bundle;
import android.os.Handler;
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
        Log.d("Mnemosyne", "on create called");
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

    @Override
    public void onConfigurationChanged(Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
        if (newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE) {
            Log.e("Mnemosyne", "ORIENTATION_LANDSCAPE");
        } else if (newConfig.orientation == Configuration.ORIENTATION_PORTRAIT) {
            Log.e("Mnemosyne", "ORIENTATION_PORTRAIT");
        }
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        Log.d("Mnemosyne", "on destroy called");
        mnemosyneThread.getHandler().post(new Runnable() {
            public void run() {
                mnemosyneThread.stopMnemosyne();
            }
        });
    }
}