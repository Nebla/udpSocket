package com.fi.uba.udpsocket;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/**
 * Created by adrian on 01/03/15.
 */
public class AlarmReceiver  extends BroadcastReceiver {

    public static final int REQUEST_CODE = 12345;
    public static final String ACTION = "com.fi.uba.udp.alarm";

    @Override
    public void onReceive(Context context, Intent intent) {
        Intent i = new Intent(context, UdpService.class);

        i.putExtra("address", intent.getStringExtra("address"));
        i.putExtra("port", intent.getIntExtra("port",0));

        context.startService(i);
    }
}
