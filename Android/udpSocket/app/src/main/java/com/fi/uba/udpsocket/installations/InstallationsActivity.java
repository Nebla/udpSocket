package com.fi.uba.udpsocket.installations;

import android.content.Context;
import android.content.Intent;
import android.net.http.AndroidHttpClient;
import android.os.AsyncTask;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.Toast;

import com.fi.uba.udpsocket.R;
import com.fi.uba.udpsocket.domain.User;
import com.fi.uba.udpsocket.login.LoginActivity;

import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.ResponseHandler;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.BasicResponseHandler;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.IOException;
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

    public void createInstallation (View view) {
        EditText resultTextView = (EditText) findViewById(R.id.installation_name_text);
        String newInstallationName = resultTextView.getText().toString();
        if (newInstallationName.isEmpty()) {
            // Fist we check for an empty name
            showError("El nombre de la instalación no puede ser vacio");
        }
        else {
            boolean found = false;
            for (String s : user.getInstallations()) {
                if (s.equals(newInstallationName)) {
                    found = true;
                    break;
                }
            }
            if (found) {
                // Here we check if there is already an installation with the same name
                showError("Ya existe una instalación con ese nombre");
            }
            else {
                // If the name isn't empty neither repeated, we create a new installation
                createNewInstallation(newInstallationName);
            }
        }
    }

    private void showError(String errorMessage) {
        Context context = getApplicationContext();
        int duration = Toast.LENGTH_SHORT;
        Toast toast = Toast.makeText(context, errorMessage, duration);
        toast.show();
    }

    private void createNewInstallation(String newInstallationName) {
        new CreateInstallationAsyncTask().execute(newInstallationName);

        /*publicKeyFile = open(installDirUnix + 'tix_key.pub','r')
        publicKey = rsa.PublicKey.load_pkcs1(publicKeyFile.read())

        # publicEncryptionKey = keygeneration.generateKeyPair(installDirUnix+'tix_key.priv',installDirUnix+'tix_key.pub')
        payload = {'user_id': str(globalUserId), 'password': globalUserPassword, 'installation_name': self.text, 'encryption_key': base64.b64encode(publicKey.save_pkcs1(format='PEM'))}
        headers = {'content-type': 'application/json'}*/
    }


    private class CreateInstallationAsyncTask extends AsyncTask<String, Void, String> {

        AndroidHttpClient httpClient = AndroidHttpClient.newInstance("");

        public CreateInstallationAsyncTask(){
        }

        @Override
        protected String doInBackground(String... params) {
            Log.i(CreateInstallationAsyncTask.class.toString(), "Create new installation for user: " + params[0]);
            String result = "";
            String url = "";
            HttpGet httpRequest = new HttpGet(url);
            JSONResponseHandler responseHandler = new JSONResponseHandler();
            try {
                result = httpClient.execute(httpRequest, responseHandler);
            } catch (IOException e) {
                e.printStackTrace();
            } catch (IllegalStateException e) {
                e.printStackTrace();
            } catch (Exception e) {
                e.printStackTrace();
            } finally {
                if (httpClient != null)
                    httpClient.close();
            }

            return result;
        }


        private class JSONResponseHandler implements ResponseHandler<String> {

            private final String ID_TAG = "id";
            private final String INSTALLATION_TAG = "installations";

            @Override
            public String handleResponse(HttpResponse response) throws ClientProtocolException, IOException {
                return "";
            }
        }
    }
}
