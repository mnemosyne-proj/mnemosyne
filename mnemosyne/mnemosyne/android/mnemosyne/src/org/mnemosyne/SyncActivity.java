package org.mnemosyne;
import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.EditText;


public class SyncActivity extends Activity {

    @Override
    public void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        setContentView(R.layout.sync);

        final EditText editDatabase = (EditText) findViewById(R.id.editDatabase);

        Button button = (Button) findViewById(R.id.syncButton);

        button.setOnClickListener(new OnClickListener() {

            public void onClick(View arg0) {
                String database = editDatabase.getText().toString();
                Intent intent = new Intent();
                intent.putExtra("DATABASE", database);

                setResult(0, intent);
                finish();
            }
        });
    }
}
