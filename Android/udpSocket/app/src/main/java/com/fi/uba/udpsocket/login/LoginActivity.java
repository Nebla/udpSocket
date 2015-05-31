package com.fi.uba.udpsocket.login;

import android.app.ProgressDialog;
import android.content.Context;
import android.content.Intent;
import android.net.http.AndroidHttpClient;
import android.os.AsyncTask;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.text.TextUtils;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.TextView;

import com.fi.uba.udpsocket.R;

import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.ResponseHandler;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.BasicResponseHandler;
import org.apache.http.impl.client.DefaultHttpClient;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;
import java.util.Map;


public class LoginActivity extends ActionBarActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);
        this.setTitle("Proyecto TiX");
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_login, menu);
        return false;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    public void login(View view) {

        TextView usernameTextView = (TextView) findViewById(R.id.username_text);
        TextView passwordTextView = (TextView) findViewById(R.id.password_text);

        new LoginAsyncTask().execute(usernameTextView.getText().toString(), passwordTextView.getText().toString());
    }

    private void update(User user) {
        Log.i(LoginActivity.class.toString(), "Successsssss");

        TextView resultTextView = (TextView) findViewById(R.id.json_response_text);
        resultTextView.setText("Id: " + user.id + "\nInstallations " + TextUtils.join(", ", user.getInstallations()));

    }

    private class User {
        private final String id;
        private final ArrayList<String> installations;

        public User(String id, ArrayList<String>installations) {
            this.id = id;
            this.installations = installations;
        }

        public String getId() {
            return this.id;
        }

        public  ArrayList<String> getInstallations() {
            return this.installations;
        }
    }


    private class LoginAsyncTask extends AsyncTask<String, Void, Void> {

        AndroidHttpClient httpClient = AndroidHttpClient.newInstance("");

        public LoginAsyncTask(){
        }

        @Override
        protected Void doInBackground(String... params) {
            Log.i(LoginAsyncTask.class.toString(), "Login for user: " + params[0]);

            String url = "http://tix.innova-red.net";
            url = url + "/bin/api/authenticate?name=" + params[0] + "&password=" + params[1];

            HttpGet httpRequest = new HttpGet(url);
            JSONResponseHandler responseHandler = new JSONResponseHandler();
            User user = null;
            try {
                user = httpClient.execute(httpRequest, responseHandler);

            } catch (ClientProtocolException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            } catch (IllegalStateException e) {
                //This exception takes place when multiple httpRequest are send in a short (very) period of time
                e.printStackTrace();
            } finally {
                if (httpClient != null)
                    httpClient.close();
            }

            update(user);
            //Intent broadcast = new Intent(ACTION_GET_POSIBLE_ADDRESSES);
            //broadcast.putStringArrayListExtra(KEY_POSSIBLE_ADDRESSES, possibileAddress);
            //Log.i(LoginAsyncTask.class.toString(), "Bradcasted...addresses");
            //for(int i = 0; i < possibileAddress.size(); i++){
            //    Log.i(GetLocationAsyncTask.class.toString(), possibileAddress.get(i));
            //}
            //mContext.sendBroadcast(broadcast);
            return null;
        }

        private class JSONResponseHandler implements ResponseHandler<User> {

            private final String ID_TAG = "id";
            private final String INSTALLATION_TAG = "installations";

            @Override
            public User handleResponse(HttpResponse response) throws ClientProtocolException, IOException {

                String userId = null;
                ArrayList<String> installations = new ArrayList<String>();

                // Server response
                String JSONResponse = new BasicResponseHandler().handleResponse(response);

                try {
                    JSONObject root = (JSONObject) new JSONTokener(JSONResponse).nextValue();

                    userId = root.getString(ID_TAG);

                    JSONArray jsonInstallations = root.getJSONArray(INSTALLATION_TAG );
                    for(int i = 0; i < jsonInstallations.length(); i++){
                        String installation = jsonInstallations.getString(i);
                        installations.add(installation.split(": ")[1]);
                    }
                } catch (JSONException e) {
                    Log.e(LoginAsyncTask.class.toString(), "Malformed json.");
                    e.printStackTrace();
                }

                return new User(userId, installations);
            }
        }
    }

}
