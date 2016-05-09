package com.fi.uba.udpsocket.screens.splash;

import android.content.Intent;
import android.content.SharedPreferences;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;

import com.fi.uba.udpsocket.R;
import com.fi.uba.udpsocket.screens.installations.CurrentInstallationActivity;
import com.fi.uba.udpsocket.screens.installations.InstallationsActivity;
import com.fi.uba.udpsocket.screens.login.LoginActivity;
import com.fi.uba.udpsocket.service.ServiceManager;
import com.fi.uba.udpsocket.utils.Connectivity;
import com.fi.uba.udpsocket.utils.PreferencesWrapper;

public class SplashActivity extends ActionBarActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash);

        String installationName = PreferencesWrapper.getInstallation(getApplicationContext());

        if (installationName != null) {
            if (Connectivity.isConnectedMobile(getApplicationContext())) {
                // Start the service if it's not already running
                ServiceManager.startService(getApplicationContext(), installationName);
            }

            // Show the installation status
            Intent intent = new Intent(this, CurrentInstallationActivity.class);
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_TASK_ON_HOME);
            startActivity(intent);
            this.finish();
        }
        else {
            // Show the login screen
            Intent intent = new Intent(this, LoginActivity.class);
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_TASK_ON_HOME);
            startActivity(intent);
            this.finish();
        }
    }
}
