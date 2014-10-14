package org.mnemosyne;

import android.app.Activity;
import android.media.AudioManager;
import android.media.MediaPlayer;
import android.media.MediaPlayer.OnCompletionListener;
import android.media.MediaPlayer.OnPreparedListener;
import android.net.Uri;
import android.os.Bundle;
import android.os.CountDownTimer;
import android.os.Handler;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.View.OnClickListener;
import android.webkit.WebView;
import android.widget.Button;
import android.widget.TextView;

import java.io.IOException;
import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class MnemosyneActivity extends Activity {

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

        MnemosyneInstaller installer = new MnemosyneInstaller(this, activityHandler);
        installer.execute();
    }

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
                        mnemosyneThread.controller._Call("show_sync_dialog");
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
        html = handleSoundFiles(html);
        question.loadDataWithBaseURL(null, html, "text/html", "utf-8", null);
    }

    public void setAnswer(String html) {
        html = handleSoundFiles(html);
        answer.loadDataWithBaseURL(null, html, "text/html", "utf-8", null);
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (mediaPlayer != null) {
            if (mediaPlayer.isPlaying()) {
                mediaPlayer.stop();
            }
            mediaPlayer.release();
            mediaPlayer = null;
        }
        mnemosyneThread.getHandler().post(new Runnable() {
            public void run() {
                mnemosyneThread.stopMnemosyne();
            }
        });
    }
}