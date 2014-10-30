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

        String server = getIntent().getStringExtra("server");
        String port = getIntent().getStringExtra("port");
        String username = getIntent().getStringExtra("username");
        String password = getIntent().getStringExtra("password");

        final EditText editServer = (EditText) findViewById(R.id.editServer);
        final EditText editPort = (EditText) findViewById(R.id.editPort);
        final EditText editUsername = (EditText) findViewById(R.id.editUsername);
        final EditText editPassword = (EditText) findViewById(R.id.editPassword);

        editServer.setText(server);
        editPort.setText(port);
        editUsername.setText(username);
        editPassword.setText(password);

        Button button = (Button) findViewById(R.id.syncButton);

        button.setOnClickListener(new OnClickListener() {

            public void onClick(View arg0) {
                Intent intent = new Intent();
                intent.putExtra("server", editServer.getText().toString() );
                intent.putExtra("port", editPort.getText().toString());
                intent.putExtra("username", editUsername.getText().toString());
                intent.putExtra("password", editPassword.getText().toString());
                setResult(RESULT_OK, intent);
                finish();
            }
        });
    }
}
