package com.fi.uba.udpsocket.service;

import android.app.ActivityManager;
import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

/**
 * Created by adrian on 18/04/16.
 */
public class ServiceManager {

    private static final String logTag = ServiceManager.class.getSimpleName();

    static public void startService(Context context, String installation) {
        Log.i(logTag, "Starting service");

        if (!isServiceRunning(context, UdpService.class)) {
            // Setup periodic alarm every 1 second
            long firstMillis = System.currentTimeMillis(); // first run of alarm is immediate
            int intervalMillis = 1000; // 1 second

            //A new execution is set
            AlarmManager alarm = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
            Intent mIntent = new Intent(context, UdpService.class);
            mIntent.putExtra("installation", installation);

            PendingIntent pendingIntent = PendingIntent.getService(context, 0, mIntent, PendingIntent.FLAG_UPDATE_CURRENT);
            alarm.setInexactRepeating(AlarmManager.RTC_WAKEUP, firstMillis, intervalMillis, pendingIntent);
        }
    }

    static public void stopService(Context context) {
        Log.i(logTag, "Stoping service");

        Intent intent = new Intent(context, UdpService.class);
        PendingIntent pendingIntent = PendingIntent.getService(context, 0,  intent, PendingIntent.FLAG_CANCEL_CURRENT);
        pendingIntent.cancel();
    }

    static private boolean isServiceRunning(Context context, Class<?> serviceClass) {
        ActivityManager manager = (ActivityManager) context.getSystemService(Context.ACTIVITY_SERVICE);
        for (ActivityManager.RunningServiceInfo service : manager.getRunningServices(Integer.MAX_VALUE)) {
            if (serviceClass.getName().equals(service.service.getClassName())) {
                Log.i(logTag, "Service already running");
                return true;
            }
        }
        Log.i(logTag, "Service not running");
        return false;
    }

}
