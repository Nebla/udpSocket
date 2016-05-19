package com.fi.uba.udpsocket.screens.installations;

import android.app.Service;
import android.content.Intent;
import android.nfc.NfcAdapter;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.fi.uba.udpsocket.R;
import com.fi.uba.udpsocket.screens.login.LoginActivity;
import com.fi.uba.udpsocket.service.ServiceManager;
import com.fi.uba.udpsocket.utils.Connectivity;
import com.fi.uba.udpsocket.utils.KeyManager;
import com.fi.uba.udpsocket.utils.PreferencesWrapper;
import com.fi.uba.udpsocket.utils.TimeLogHelper;

public class CurrentInstallationActivity extends ActionBarActivity {

    private String installationName;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_current_installation);

        installationName = PreferencesWrapper.getInstallation(getApplicationContext());

        TextView installationTextView = (TextView) findViewById(R.id.installation_name);
        installationTextView.setText(installationName);

        boolean isRunning = ServiceManager.isServiceRunning(getApplicationContext());
        this.setButtonsState(isRunning);
    }

    private void setButtonsState(boolean isRunning) {
        Button startButton = (Button) findViewById(R.id.start_service_action);
        Button stopButton = (Button) findViewById(R.id.stop_service_action);
        startButton.setEnabled(!isRunning);
        stopButton.setEnabled(isRunning);
    }

    public void stopService(View view) {
        ServiceManager.stopService(getApplicationContext());
        this.setButtonsState(false);
    }

    public void startService(View view) {
        /*if (Connectivity.isConnectedMobile(getApplicationContext())) {
            ServiceManager.startService(getApplicationContext(), installationName);
            this.setButtonsState(true);
        }
        else {

        }*/
    }

    public void deleteCurrentInstallation(View view) {
        ServiceManager.stopService(getApplicationContext());
        PreferencesWrapper.removeInstallation(getApplicationContext());
        KeyManager.removeKeys(getApplicationContext(), installationName);
        TimeLogHelper.deleteAllFiles(getApplicationContext());

        Intent intent = new Intent(this, LoginActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_TASK_ON_HOME);
        startActivity(intent);
        this.finish();
    }
}
