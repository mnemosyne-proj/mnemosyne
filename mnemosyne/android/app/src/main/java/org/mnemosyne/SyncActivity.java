package org.mnemosyne;
import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.CheckBox;
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
        boolean rememberPassword = getIntent().getBooleanExtra("rememberPassword", true);

        final EditText editServer = (EditText) findViewById(R.id.editServer);
        final EditText editPort = (EditText) findViewById(R.id.editPort);
        final EditText editUsername = (EditText) findViewById(R.id.editUsername);
        final EditText editPassword = (EditText) findViewById(R.id.editPassword);
        final CheckBox checkRememberPassword = (CheckBox) findViewById(R.id.checkRememberPassword);

        editServer.setText(server);
        editPort.setText(port);
        editUsername.setText(username);
        editPassword.setText(password);
        checkRememberPassword.setChecked(rememberPassword);

        Button button = (Button) findViewById(R.id.syncButton);

        button.setOnClickListener(new OnClickListener() {

            public void onClick(View arg0) {
                Intent intent = new Intent();
                intent.putExtra("server", editServer.getText().toString().trim());
                intent.putExtra("port", editPort.getText().toString().trim());
                intent.putExtra("username", editUsername.getText().toString().trim());
                intent.putExtra("password", editPassword.getText().toString().trim());
                intent.putExtra("rememberPassword", checkRememberPassword.isChecked());
                setResult(RESULT_OK, intent);
                finish();
            }
        });
    }
}
