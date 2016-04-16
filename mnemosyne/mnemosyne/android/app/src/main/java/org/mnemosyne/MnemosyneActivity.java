package org.mnemosyne;

import android.annotation.TargetApi;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.Configuration;
import android.media.AudioManager;
import android.media.MediaPlayer;
import android.media.MediaPlayer.OnCompletionListener;
import android.media.MediaPlayer.OnPreparedListener;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.CountDownTimer;
import android.os.Handler;
import android.support.v4.view.WindowCompat;
import android.support.v7.app.ActionBar;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.GestureDetector;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.MotionEvent;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.Window;
import android.webkit.WebView;
import android.widget.Button;
import android.widget.TextView;

import java.io.IOException;
import java.util.ArrayList;
import java.util.concurrent.TimeUnit;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;

public class MnemosyneActivity extends AppCompatActivity {

    public static final int SYNC_ACTIVITY_RESULT = 0;
    public static final int ACTIVATE_CARDS_ACTIVITY_RESULT = 1;

    String currentHtml;
    MediaPlayer mediaPlayer = null;
    ArrayList<Uri> soundFiles = new ArrayList<Uri>();
    ArrayList<Integer> starts = new ArrayList<Integer>();
    ArrayList<Integer> stops = new ArrayList<Integer>();
    int soundIndex = -1;

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

    GestureDetector gestureDetector;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);

        Toolbar myToolbar = (Toolbar) findViewById(R.id.my_toolbar);
        setSupportActionBar(myToolbar);
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

        question.getSettings().setJavaScriptEnabled(true);
        answer.getSettings().setJavaScriptEnabled(true);

        MnemosyneInstaller installer = new MnemosyneInstaller(this, activityHandler);
        installer.execute();
    }

    @TargetApi(Build.VERSION_CODES.KITKAT)
    public void continueOnCreate() {

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

        // Does not work yet as expected, since the webview has its own handling of
        // gestures to deal with scrolling
        //http://stackoverflow.com/questions/7774642/scroll-webview-horizontally-inside-a-viewpager
        gestureDetector = new GestureDetector(this, new MyGestureListener());

        // First run wizard.
        SharedPreferences settings = getSharedPreferences("UserInfo", 0);
        if (!settings.contains("shown_first_run_wizard")) {
            AlertDialog.Builder alert = new AlertDialog.Builder(this);
            alert.setMessage("This application is meant to be used in conjunction with the Mnemosyne desktop app (http://www.mnemosyne-proj.org). Input your cards there, start the sync server in 'Configure Mnemosyne' and then you can sync and review the cards in this Android app. IMPORTANT: note that only the database 'default.db' is synced.");
            alert.setCancelable(false);
            alert.setPositiveButton("OK", new DialogInterface.OnClickListener() {
                public void onClick(DialogInterface dialog, int whichButton) {
                    mnemosyneThread.getHandler().post(new Runnable() {
                        public void run() {
                            mnemosyneThread.controller._Call("show_sync_dialog_pre");
                        }
                    });
                }
            });
            alert.show();

            SharedPreferences.Editor editor = settings.edit();
            editor.putBoolean("shown_first_run_wizard", true);
            editor.commit();
        }
    }

    @Override
    @TargetApi(Build.VERSION_CODES.KITKAT)
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if ((hasFocus) && (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT)) {
            getWindow().getDecorView().setSystemUiVisibility(
                    View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                            | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                            | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                            | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                            | View.SYSTEM_UI_FLAG_FULLSCREEN
                            | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);}
    }


    @Override
    public boolean onCreateOptionsMenu(Menu menu)
    {
        MenuInflater menuInflater = getMenuInflater();
        menuInflater.inflate(R.layout.menu, menu);
        return true;
    }
    
    @Override
    public boolean onOptionsItemSelected(MenuItem item)
    {
        switch (item.getItemId())
        {
            case R.id.menu_sync:
                mnemosyneThread.getHandler().post(new Runnable() {
                    public void run() {
                        mnemosyneThread.controller._Call("show_sync_dialog_pre");
                    }
                });
                return true;

            case R.id.menu_replay_media:
                handleSoundFiles(currentHtml);
                return true;

            case R.id.menu_star:
                mnemosyneThread.getHandler().post(new Runnable() {
                    public void run() {
                        mnemosyneThread.controller._Call("star_current_card");
                    }
                });
                return true;

            case R.id.menu_activate:
                mnemosyneThread.getHandler().post(new Runnable() {
                    public void run() {
                        mnemosyneThread.controller._Call("show_activate_cards_dialog_pre");
                    }
                });
                return true;

            default:
                return super.onOptionsItemSelected(item);
        }
    }

    public void playNextSound() {
        if (mediaPlayer != null) {
            mediaPlayer.release();
        }
        mediaPlayer = new MediaPlayer();
        mediaPlayer.setAudioStreamType(AudioManager.STREAM_MUSIC);

        try {
            mediaPlayer.setDataSource(getApplicationContext(), soundFiles.get(soundIndex));
        } catch (IllegalArgumentException e) {
            e.printStackTrace();
        } catch (SecurityException e) {
            e.printStackTrace();
        } catch (IllegalStateException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

        mediaPlayer.setOnPreparedListener(new OnPreparedListener() {
            public void onPrepared(MediaPlayer mp) {
                mp.seekTo(starts.get(soundIndex));
                mp.start();
                if (stops.get(soundIndex) != 0)
                {
                    final MediaPlayer _mp = mp;
                    int duration = stops.get(soundIndex) - starts.get(soundIndex);
                    new CountDownTimer(duration, 100) {
                        @Override
                        public void onFinish() {
                            _mp.release();
                            soundIndex++;
                            if (soundIndex < soundFiles.size()) {
                                playNextSound();
                            }
                        }

                        @Override
                        public void onTick(long millisUntilFinished) {}
                    }.start();
                }
            }
        });

        mediaPlayer.setOnCompletionListener(new OnCompletionListener() {
            public void onCompletion(MediaPlayer mp) {
                soundIndex++;
                if (soundIndex < soundFiles.size()) {
                    playNextSound();
                }
                else {
                    mp.release();
                    mp = null;
                }
            }
        });

        mediaPlayer.prepareAsync();
    }

    Pattern audioRE = Pattern.compile("<audio src=\"(.+?)\"(.*?)>",
            Pattern.CASE_INSENSITIVE | Pattern.DOTALL);
    Pattern startRE = Pattern.compile("start=\"(.+?)\"",
            Pattern.CASE_INSENSITIVE | Pattern.DOTALL);
    Pattern stopRE = Pattern.compile("stop=\"(.+?)\"",
            Pattern.CASE_INSENSITIVE | Pattern.DOTALL);

    public String handleSoundFiles(String html) {
        if (mediaPlayer != null) {
            mediaPlayer.release();
        }
        soundFiles.clear();
        starts.clear();
        stops.clear();
        Matcher matcher = audioRE.matcher(html);
        while (matcher.find()) {
            // Look for start and stop of sound segment in ms.
            int start = 0;
            int stop = 0;
            if (matcher.group(2) != null) {

                Matcher startMatcher = startRE.matcher(matcher.group(2));
                while (startMatcher.find()) {
                    start = (int) (Double.valueOf(startMatcher.group(1)).doubleValue() * 1000);
                    break;
                }

                Matcher stopMatcher = stopRE.matcher(matcher.group(2));
                while (stopMatcher.find()) {
                    stop = (int) (Double.valueOf(stopMatcher.group(1)).doubleValue() * 1000);
                    break;
                }
            }

            soundFiles.add(Uri.parse(matcher.group(1)));
            starts.add(start);
            stops.add(stop);
            soundIndex = 0;

            playNextSound();
        }

        return matcher.replaceAll("");
    }

    public void setQuestion(String html) {
        currentHtml = html;
        html = handleSoundFiles(html);
        question.loadDataWithBaseURL(null, html, "text/html", "utf-8", null);
    }

    public void setAnswer(String html, Boolean processAudio) {
        if (processAudio == true) {
            currentHtml = html;
            html = handleSoundFiles(html);
        }
        answer.loadDataWithBaseURL(null, html, "text/html", "utf-8", null);
    }

    // Get results back from sync activity.

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data)
    {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == SYNC_ACTIVITY_RESULT) {
            if (resultCode == RESULT_OK) {
                final String server = data.getStringExtra("server");
                final Integer port = new Integer(data.getStringExtra("port"));
                final String username = data.getStringExtra("username");
                final String password = data.getStringExtra("password");

                mnemosyneThread.getHandler().post(new Runnable() {
                    public void run() {
                        mnemosyneThread.config._Call("__setitem__", "server_for_sync_as_client", server);
                        mnemosyneThread.config._Call("__setitem__", "port_for_sync_as_client", port);
                        mnemosyneThread.config._Call("__setitem__", "username_for_sync_as_client", username);
                        mnemosyneThread.config._Call("__setitem__", "password_for_sync_as_client", password);
                        mnemosyneThread.config._Call("save");
                        mnemosyneThread.controller._Call("sync", server, port, username, password);
                        mnemosyneThread.controller._Call("show_sync_dialog_post");
                    }
                });
            }
            else {
                mnemosyneThread.getHandler().post(new Runnable() {
                    public void run() {
                        mnemosyneThread.controller._Call("show_sync_dialog_post");
                    }
                });
            }
        }

        if (requestCode == ACTIVATE_CARDS_ACTIVITY_RESULT) {
            if (resultCode == RESULT_OK) {
                final String savedSet = data.getStringExtra("saved_set");
                mnemosyneThread.getHandler().post(new Runnable() {
                    public void run() {
                        mnemosyneThread.setProgressText("(De)activating cards...");
                        mnemosyneThread.activateCardsDialog._Call("set_criterion_with_name", savedSet);
                        mnemosyneThread.controller._Call("show_activate_cards_dialog_post");
                        mnemosyneThread.closeProgress();
                    }
                });
            }
            else {
                mnemosyneThread.getHandler().post(new Runnable() {
                    public void run() {
                        mnemosyneThread.controller._Call("show_activate_cards_dialog_post");
                    }
                });
            }
        }
    }

    @Override
    public void onPause() {
        super.onPause();
        try {
            if (mediaPlayer != null) {
                if (mediaPlayer.isPlaying()) {
                    mediaPlayer.stop();
                }
                mediaPlayer.reset();
                mediaPlayer.release();
                mediaPlayer = null;
            }
        } catch(Exception e){
        }
        mnemosyneThread.getHandler().post(new Runnable() {
            public void run() {
                mnemosyneThread.pauseMnemosyne();
            }
        });
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        try {
            if (mediaPlayer != null) {
                if (mediaPlayer.isPlaying()) {
                    mediaPlayer.stop();
                }
                mediaPlayer.reset();
                mediaPlayer.release();
                mediaPlayer = null;
            }
        } catch (Exception e){
        }
        mnemosyneThread.getHandler().post(new Runnable() {
            public void run() {
                mnemosyneThread.stopMnemosyne();
            }
        });

    }

    @Override
    public boolean onTouchEvent(MotionEvent event){
        Log.d("Mnemosyne", "Touchevent" + event);
        this.gestureDetector.onTouchEvent(event);
        return super.onTouchEvent(event);
    }

    class MyGestureListener extends GestureDetector.SimpleOnGestureListener {

        private static final int SWIPE_MIN_DISTANCE = 120;
        private static final int SWIPE_MAX_OFF_PATH = 200;
        private static final int SWIPE_THRESHOLD_VELOCITY = 200;

        @Override
        public boolean onDown(MotionEvent e) {
            return true;
        }

        @Override
        public boolean onFling(MotionEvent e1, MotionEvent e2,
                float velocityX, float velocityY) {
            Log.d("Mnemosyne", "onFling: " + e1.toString()+e2.toString());

            try {
                float diffAbs = Math.abs(e1.getY() - e2.getY());
                float diff = e1.getX() - e2.getX();

                if (diffAbs > SWIPE_MAX_OFF_PATH)
                    return false;

                // Left swipe.
                if (diff > SWIPE_MIN_DISTANCE
                        && Math.abs(velocityX) > SWIPE_THRESHOLD_VELOCITY) {
                    MnemosyneActivity.this.onLeftSwipe();
                    return true;

                    // Right swipe.
                } else if (-diff > SWIPE_MIN_DISTANCE
                        && Math.abs(velocityX) > SWIPE_THRESHOLD_VELOCITY) {
                    MnemosyneActivity.this.onRightSwipe();
                    return true;
                }
            } catch (Exception e) {
                Log.e("Mnemosyne", "Error on gestures");
            }
            return false;
        }
    }

    public void onLeftSwipe() {
        Log.d("Mnemosyne", "left swipe");
    }

    public void onRightSwipe() {
        Log.d("Mnemosyne", "right swipe");
    }

}