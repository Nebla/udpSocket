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

    static public void startService(Context context, String installation) {
        Log.i("Service Manager", "Starting service");

        // Construct an intent that will execute the AlarmReceiver
        //Intent intent = new Intent(context, AlarmReceiver.class);
        //intent.putExtra("installation",installation);

        // Create a PendingIntent to be triggered when the alarm goes off
        //final PendingIntent pIntent = PendingIntent.getBroadcast(context, AlarmReceiver.REQUEST_CODE,
        //        intent, PendingIntent.FLAG_UPDATE_CURRENT);

        // Setup periodic alarm every 1 second
        long firstMillis = System.currentTimeMillis(); // first run of alarm is immediate
        int intervalMillis = 1000; // 1 second
        //AlarmManager alarm = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        //alarm.setInexactRepeating(AlarmManager.RTC_WAKEUP, firstMillis, intervalMillis, pIntent);

        //A new execution is set
        AlarmManager alarm = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        Intent mIntent = new Intent(context, UdpService.class);
        mIntent.putExtra("installation",installation);

        PendingIntent pendingIntent = PendingIntent.getService(context, 0,  mIntent, PendingIntent.FLAG_UPDATE_CURRENT);
        alarm.setInexactRepeating(AlarmManager.RTC_WAKEUP, firstMillis, intervalMillis, pendingIntent);

    }

    static public void stopService(Context context) {
        AlarmManager alarm = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);

        Intent intent = new Intent(context, UdpService.class);
        PendingIntent pendingIntent = PendingIntent.getService(context, 0,  intent, PendingIntent.FLAG_UPDATE_CURRENT);

        alarm.cancel(pendingIntent);
    }

    private boolean isServiceRunning(Context context, Class<?> serviceClass) {
        ActivityManager manager = (ActivityManager) context.getSystemService(Context.ACTIVITY_SERVICE);
        for (ActivityManager.RunningServiceInfo service : manager.getRunningServices(Integer.MAX_VALUE)) {
            if (serviceClass.getName().equals(service.service.getClassName())) {
                return true;
            }
        }
        return false;
    }

}
