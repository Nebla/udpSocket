package com.fi.uba.udpsocket.receiver;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.util.Log;

public class BootBroadcastReceiver extends BroadcastReceiver {

    @Override
    public void onReceive(Context context, Intent intent) {
        Log.i("BootBroadcastReceiver", "Boot complete recieved");
        SharedPreferences prefs = context.getSharedPreferences("InstallationPreferences", Context.MODE_PRIVATE);
        String installationName = prefs.getString("Installation", null);
        if (installationName != null) {
            // Show the installation status
            Log.i("BootBroadcastReceiver", "Installation "+installationName+" found");
            //ServiceManager.startService(context,installationName);
        }
        else {
            Log.i("BootBroadcastReceiver", "Installation NOT found");
        }
    }
}
