package com.fi.uba.udpsocket.service;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

/**
 * Created by adrian on 01/03/15.
 */
public class AlarmReceiver extends BroadcastReceiver {

    public static final int REQUEST_CODE = 12345;
    public static final String ACTION = "com.fi.uba.udp.alarm";

    @Override
    public void onReceive(Context context, Intent intent) {

        Log.i("Alarm Receiver", "Received alarm");

        Intent i = new Intent(context, UdpService.class);

        i.putExtra("installation", intent.getStringExtra("installation"));
        i.putExtra("address", intent.getStringExtra("address"));
        i.putExtra("port", intent.getIntExtra("port", 0));

        context.startService(i);
    }
}
