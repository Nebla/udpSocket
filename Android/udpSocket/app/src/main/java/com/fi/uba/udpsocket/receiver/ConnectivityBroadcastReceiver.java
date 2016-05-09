package com.fi.uba.udpsocket.receiver;

import com.fi.uba.udpsocket.service.ServiceManager;
import com.fi.uba.udpsocket.utils.Connectivity;
import com.fi.uba.udpsocket.utils.PreferencesWrapper;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;

/**
 * Created by adrian on 4/29/16.
 */
public class ConnectivityBroadcastReceiver extends BroadcastReceiver {

    private static final String logTag = ConnectivityBroadcastReceiver.class.getSimpleName();

    @Override
    public void onReceive(Context context, Intent intent) {
        Log.i(logTag, "Connectivity changed");

        /*Log.i(logTag, "action: " + intent.getAction());
        Log.i(logTag, "component: " + intent.getComponent());

        Bundle extras = intent.getExtras();
        if (extras != null) {
            for (String key: extras.keySet()) {
                Log.i(logTag, "key [" + key + "]: " +
                        extras.get(key));
            }
        }
        else {
            Log.i(logTag, "no extras");
        }*/

        if (Connectivity.isConnectedMobile(context)) {
            Log.i(logTag, "MOBILE");
            String installationName = PreferencesWrapper.getInstallation(context);
            if (installationName != null) {
                Log.i(logTag, "Installation "+installationName+" found");
                ServiceManager.startService(context, installationName);
            }
        }
        else {
            Log.i(logTag, "NOT MOBILE");
            ServiceManager.stopService(context);
        }

    }
}
