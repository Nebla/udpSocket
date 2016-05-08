package com.fi.uba.udpsocket;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.EditText;

import com.fi.uba.udpsocket.service.ServiceManager;
import com.fi.uba.udpsocket.utils.KeyManager;

public class UdpActivity extends Activity {
    public final static String EXTRA_MESSAGE = "com.fi.uba.udpSocket.MESSAGE";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_udp);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_udp, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();
        return id == R.id.action_settings || super.onOptionsItemSelected(item);
    }

    /* Called when the user clicks the Send button */
    public void sendMessage(View view) {

        EditText editText = (EditText) findViewById(R.id.edit_message);
        String message = editText.getText().toString();

        EditText portText = (EditText) findViewById(R.id.edit_port);
        String port = portText.getText().toString();

        EditText ipText = (EditText) findViewById(R.id.edit_address);
        String ipAddress = ipText.getText().toString();


        ConnectSocketAsyncTask task = new ConnectSocketAsyncTask();
        task.execute(ipAddress, port, message);
    }

    public void createInstallation (View view) {

        EditText editText = (EditText) findViewById(R.id.edit_message);
        String instName = editText.getText().toString();

        KeyManager.generateKeys(getApplicationContext(), instName);

        String result = KeyManager.getBase64EncodedPemPublicKey(getApplicationContext(), instName);
        Log.i("UdpActivity - Create installation", result);
    }

    public void startService(View view) {
        ServiceManager.startService(getApplicationContext(),"TestInstallation");
    }

    public void stopService(View view) {
        ServiceManager.stopService(getApplicationContext());
    }
}
