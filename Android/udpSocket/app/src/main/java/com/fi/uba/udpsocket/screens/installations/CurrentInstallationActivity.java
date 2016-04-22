package com.fi.uba.udpsocket.screens.installations;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.view.View;

import com.fi.uba.udpsocket.R;
import com.fi.uba.udpsocket.service.AlarmReceiver;
import com.fi.uba.udpsocket.service.ServiceManager;

public class CurrentInstallationActivity extends ActionBarActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_current_installation);

        SharedPreferences prefs = getSharedPreferences("InstallationPreferences", MODE_PRIVATE);
        String installationName = prefs.getString("Installation", null);
        ServiceManager.startService(getApplicationContext(),installationName);
    }

    public void stopService(View view) {
        Intent intent = new Intent(getApplicationContext(), AlarmReceiver.class);
        final PendingIntent pIntent = PendingIntent.getBroadcast(this, AlarmReceiver.REQUEST_CODE, intent, PendingIntent.FLAG_UPDATE_CURRENT);
        AlarmManager alarm = (AlarmManager) this.getSystemService(Context.ALARM_SERVICE);
        alarm.cancel(pIntent);
    }
}
