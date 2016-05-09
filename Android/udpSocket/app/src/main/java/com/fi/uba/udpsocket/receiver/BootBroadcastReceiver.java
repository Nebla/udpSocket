package com.fi.uba.udpsocket.receiver;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

import com.fi.uba.udpsocket.R;
import com.fi.uba.udpsocket.service.ServiceManager;
import com.fi.uba.udpsocket.utils.Connectivity;
import com.fi.uba.udpsocket.utils.PreferencesWrapper;

public class BootBroadcastReceiver extends BroadcastReceiver {

    private static final String logTag = BootBroadcastReceiver.class.getSimpleName();

    @Override
    public void onReceive(Context context, Intent intent) {

        Log.i(logTag, "Boot complete recieved");

        String installationName = PreferencesWrapper.getInstallation(context);

        if (installationName != null) {
            Log.i(logTag, "Installation "+installationName+" found");

            if (Connectivity.isConnectedMobile(context)) {
                Log.i(logTag, "MOBILE Connection");
                ServiceManager.startService(context, installationName);
            }
        }
        else {
            Log.i("BootBroadcastReceiver", "Installation NOT found");
        }
    }
}
