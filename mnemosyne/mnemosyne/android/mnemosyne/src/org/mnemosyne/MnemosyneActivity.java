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

    public Handler activityHandler = new Handler();
    private Thread mnemosyneThread;

    private Button button0;
    private Button button1;
    private Button button2;
    private Button button3;
    private Button button4;
    private Button button5;

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

        mnemosyneThread = new Thread(MnemosyneThread(activityHandler));
        mnemosyneThread.start();

        showAnswerButton.setOnClickListener(new OnClickListener() {

            public void onClick(View view) {
                Log.d("Mnemosyne", "show_answer clicked ");
                reviewController._Call("show_answer");
            }
        });

        button0.setOnClickListener(new OnClickListener() {

            public void onClick(View view) {
                reviewController._Call("grade_answer", 0);
            }
        });

        button1.setOnClickListener(new OnClickListener() {

            public void onClick(View view) {
                reviewController._Call("grade_answer", 1);
            }
        });

        button2.setOnClickListener(new OnClickListener() {

            public void onClick(View view) {
                reviewController._Call("grade_answer", 2);
            }
        });

        button3.setOnClickListener(new OnClickListener() {

            public void onClick(View view) {
                reviewController._Call("grade_answer", 3);
            }
        });

        button4.setOnClickListener(new OnClickListener() {

            public void onClick(View view) {
                reviewController._Call("grade_answer", 4);
            }
        });

        button5.setOnClickListener(new OnClickListener() {

            public void onClick(View view) {
                reviewController._Call("grade_answer", 5);
            }
        });

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

    public void setQuestionBoxVisible(boolean isVisible) {
        if (isVisible) {
            question.setVisibility(android.view.View.VISIBLE);
            questionLabel.setVisibility(android.view.View.VISIBLE);
        }
        else {
            question.setVisibility(android.view.View.GONE);
            questionLabel.setVisibility(android.view.View.GONE);
        }
    }

    public void setAnswerBoxVisible(boolean isVisible) {
        if (isVisible) {
            answer.setVisibility(android.view.View.VISIBLE);
            answerLabel.setVisibility(android.view.View.VISIBLE);
        }
        else {
            answer.setVisibility(android.view.View.GONE);
            answerLabel.setVisibility(android.view.View.GONE);
        }
    }

    public void updateShowButton(String text, boolean isDefault, boolean isEnabled) {
        showAnswerButton.setText(text);
        if (isEnabled) {
            showAnswerButton.setVisibility(android.view.View.VISIBLE);
        }
        else {
            showAnswerButton.setVisibility(android.view.View.GONE);
        }
    }

    public void setGradesEnabled(boolean isEnabled) {
        if (isEnabled) {
            button0.setVisibility(android.view.View.VISIBLE);
            button1.setVisibility(android.view.View.VISIBLE);
            button2.setVisibility(android.view.View.VISIBLE);
            button3.setVisibility(android.view.View.VISIBLE);
            button4.setVisibility(android.view.View.VISIBLE);
            button5.setVisibility(android.view.View.VISIBLE);
        }
        else {
            button0.setVisibility(android.view.View.GONE);
            button1.setVisibility(android.view.View.GONE);
            button2.setVisibility(android.view.View.GONE);
            button3.setVisibility(android.view.View.GONE);
            button4.setVisibility(android.view.View.GONE);
            button5.setVisibility(android.view.View.GONE);
        }
    }

    String statusBarText;

    public void setStatusbarText(String text) {
        Log.d("Mnemosyne", "setstatusbartex " + text);
        statusBarText = text;
        handler.post(new Runnable() {
            public void run() {
                statusbar.setText(statusBarText);
            }});
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

        handler.post(new Runnable() {
            public void run() {
                progressDialog.setProgress(progressValue);
                Log.d("Mnemosyne", "handler " + progressValue);
            }
        });
    }

    public void closeProgress() {
        progressDialog.dismiss();
    }

    public void testProgress() {
        Log.d("Mnemosyne", "testProgress ");

        handler.post(new Runnable() {
            public void run() {
                Log.d("Mnemosyne", "runnable creating ui");
                setProgressText("progress2");
                setProgressRange(3);
            }
        });

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


    //--------------------------
    void sendMsgToThread()
    {
        Message msg = mThread.getHandler().obtainMessage();
        myB.putInt("MAIN DELIVERY", 321);
        msg.setData(myB);
        mThread.getHandler().sendMessage(msg);
    }
}
//=========================================================================================
//=========================================================================================

public class MyThread extends Thread{
    //Properties:
    private final   String TAG = "MyThread";            //Log tag
    private         Handler outHandler;                 //handles the OUTgoing msgs
    Bundle          myB = new Bundle();                 //used for creating the msgs
    private         Handler inHandler = new Handler(){  //handles the INcoming msgs
        @Override public void handleMessage(Message msg)
        {
            myB = msg.getData();
            Log.i(TAG, "Handler got message"+ myB.getInt("MAIN DELIVERY"));
        }
    };

    //Methods:
    //--------------------------
    @Override
    public void run(){
        sendMsgToMainThread();  //send to the main activity a msg
        Looper.prepare();
        Looper.loop();
        //after this line nothing happens because of the LOOP!
        Log.i(TAG, "Lost message");
    }
    //--------------------------
    public MyThread(Handler mHandler) {
        //C-tor that get a reference object to the MainActivity handler.
        //this is how we know to whom we need to connect with.
        outHandler = mHandler;
    }
    //--------------------------
    public Handler getHandler(){
        //a Get method which return the handler which This Thread is connected with.
        return inHandler;
    }
    //--------------------------
    private void sendMsgToMainThread(){
        Message msg = outHandler.obtainMessage();
        myB.putInt("THREAD DELIVERY", 123);
        msg.setData(myB);
        outHandler.sendMessage(msg);
    }

};