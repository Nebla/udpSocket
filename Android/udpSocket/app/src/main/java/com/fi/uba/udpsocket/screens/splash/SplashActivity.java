package com.fi.uba.udpsocket.screens.splash;

import android.content.Intent;
import android.content.SharedPreferences;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;

import com.fi.uba.udpsocket.R;
import com.fi.uba.udpsocket.screens.installations.CurrentInstallationActivity;
import com.fi.uba.udpsocket.screens.installations.InstallationsActivity;
import com.fi.uba.udpsocket.screens.login.LoginActivity;

public class SplashActivity extends ActionBarActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash);

        SharedPreferences prefs = getSharedPreferences("InstallationPreferences", MODE_PRIVATE);
        String installationName = prefs.getString("Installation", null);
        if (installationName != null) {
            // Show the installation status
            Intent intent = new Intent(this, CurrentInstallationActivity.class);
            startActivity(intent);
        }
        else {
            // Show the login screen
            Intent intent = new Intent(this, LoginActivity.class);
            startActivity(intent);
        }
    }
}
