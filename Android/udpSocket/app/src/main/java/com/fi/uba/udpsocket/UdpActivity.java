package com.fi.uba.udpsocket;

import android.app.Activity;
import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.EditText;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.net.InetAddress;
import java.net.UnknownHostException;

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

        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }


    /** Called when the user clicks the Send button */
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

    public void startService(View view) {

        Log.i("UdpActivity","Startin service");

        EditText portText = (EditText) findViewById(R.id.edit_port);
        String portString = portText.getText().toString();
        int port;
        try {
            port = Integer.parseInt(portString);
        } catch (NumberFormatException e) {
            e.printStackTrace();
            Log.e("UdpActivity", "Invalid port number");
            return;
        }

        EditText ipText = (EditText) findViewById(R.id.edit_address);
        String ipAddress = ipText.getText().toString();
        try {
            InetAddress.getByName(ipAddress);
        } catch (UnknownHostException e) {
            e.printStackTrace();
            Log.e("UdpActivity", "Invalid ip address");
            return;
        }


        // Construct an intent that will execute the AlarmReceiver
        Intent intent = new Intent(getApplicationContext(), AlarmReceiver.class);

        intent.putExtra("address",ipAddress);
        intent.putExtra("port",port);

        // Create a PendingIntent to be triggered when the alarm goes off
        final PendingIntent pIntent = PendingIntent.getBroadcast(this, AlarmReceiver.REQUEST_CODE,
                intent, PendingIntent.FLAG_UPDATE_CURRENT);

        // Setup periodic alarm every 20 seconds
        long firstMillis = System.currentTimeMillis(); // first run of alarm is immediate
        int intervalMillis = 20000; // 20 seconds
        AlarmManager alarm = (AlarmManager) this.getSystemService(Context.ALARM_SERVICE);
        alarm.setInexactRepeating(AlarmManager.RTC_WAKEUP, firstMillis, intervalMillis, pIntent);
    }

    public void stopService(View view) {
        Intent intent = new Intent(getApplicationContext(), AlarmReceiver.class);
        final PendingIntent pIntent = PendingIntent.getBroadcast(this, AlarmReceiver.REQUEST_CODE, intent, PendingIntent.FLAG_UPDATE_CURRENT);
        AlarmManager alarm = (AlarmManager) this.getSystemService(Context.ALARM_SERVICE);
        alarm.cancel(pIntent);

        /* Test generated file */
        TextView textView = (TextView) findViewById(R.id.fileTest);
        StringBuilder builder = null;
        BufferedReader bufferedReader = null;
        try {
            bufferedReader = new BufferedReader(new FileReader(new
                    File(getFilesDir()+ File.separator+"saraza")));

            String read;
            builder = new StringBuilder("");
            while((read = bufferedReader.readLine()) != null){
                builder.append(read);
            }
            bufferedReader.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

        Log.d("Output", builder.toString());
        textView.setText(builder.toString());
    }
}
