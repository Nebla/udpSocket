package com.fi.uba.udpsocket.installations;

import android.content.Intent;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;

import com.fi.uba.udpsocket.R;
import com.fi.uba.udpsocket.domain.User;
import com.fi.uba.udpsocket.login.LoginActivity;

import java.util.ArrayList;

public class InstallationsActivity extends ActionBarActivity {

    private User user;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_installations);
        this.setTitle("Installations");

        Intent i = getIntent();
        user = i.getParcelableExtra(LoginActivity.USER_MESSAGE);

        /*TextView resultTextView = (TextView) findViewById(R.id.installation_name_text);
        String userId = user.getId();
        ArrayList<String> installations = user.getInstallations();
        resultTextView.setText("Id: " + userId + "\nInstallations:\n " + TextUtils.join(", ", installations));*/

        ListView listView = (ListView) findViewById(R.id.installations_list);
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this,
                android.R.layout.simple_list_item_1, user.getInstallations());
        listView.setAdapter(adapter);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_installations, menu);
        return false;
    }

}
