package com.fi.uba.udpsocket.login;

import android.app.ProgressDialog;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.net.http.AndroidHttpClient;
import android.os.AsyncTask;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.text.TextUtils;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
import android.widget.TextView;
import android.widget.Toast;

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

        TextView usernameTextView = (TextView) findViewById(R.id.username_text);
        TextView passwordTextView = (TextView) findViewById(R.id.password_text);
        usernameTextView.setText("adrianmdu@gmail.com");
        passwordTextView.setText("celeste6");
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

    public void createAccount(View view) {
        /*Intent intent = new Intent(this, CreateActivity.class);
        startActivity(intent);*/

        String baseUrl = getResources().getString(R.string.tix_base_url);
        String createAccount = getResources().getString(R.string.tix_create_url);
        Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse(baseUrl + "/" + createAccount));
        startActivity(browserIntent);
    }

    public void login(View view) {

        TextView usernameTextView = (TextView) findViewById(R.id.username_text);
        TextView passwordTextView = (TextView) findViewById(R.id.password_text);

        InputMethodManager imm = (InputMethodManager)getSystemService(Context.INPUT_METHOD_SERVICE);
        imm.hideSoftInputFromWindow(usernameTextView.getWindowToken(), 0);
        imm.hideSoftInputFromWindow(passwordTextView.getWindowToken(), 0);

        new LoginAsyncTask().execute(usernameTextView.getText().toString(), passwordTextView.getText().toString());
    }

    private void update(User user) {
        Log.i(LoginActivity.class.toString(), "Successsssss");

        if (user != null) {
            TextView resultTextView = (TextView) findViewById(R.id.json_response_text);

            String userId = user.getId();
            ArrayList<String> installations = user.getInstallations();

            resultTextView.setText("Id: " + userId + "\nInstallations:\n " + TextUtils.join(", ", installations));
        }
        else {
            Context context = getApplicationContext();
            CharSequence text = "Usuario o contraseña invalidos";
            int duration = Toast.LENGTH_SHORT;
            Toast toast = Toast.makeText(context, text, duration);
            toast.show();
        }
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


    private class LoginAsyncTask extends AsyncTask<String, Void, User> {

        AndroidHttpClient httpClient = AndroidHttpClient.newInstance("");

        public LoginAsyncTask(){
        }

        @Override
        protected User doInBackground(String... params) {
            Log.i(LoginAsyncTask.class.toString(), "Login for user: " + params[0]);

            String url = "http://tix.innova-red.net";
            url = url + "/bin/api/authenticate?name=" + params[0] + "&password=" + params[1];

            HttpGet httpRequest = new HttpGet(url);
            JSONResponseHandler responseHandler = new JSONResponseHandler();
            User user = null;
            try {
                user = httpClient.execute(httpRequest, responseHandler);
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

            return user;
        }

        @Override
        protected void onPostExecute(User user) {
            update(user);
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

                    if (root.has(ID_TAG)) {
                        userId = root.getString(ID_TAG);
                    } else {
                        return null;
                    }

                    if (root.has(INSTALLATION_TAG)) {
                        JSONArray jsonInstallations = root.getJSONArray(INSTALLATION_TAG );
                        for(int i = 0; i < jsonInstallations.length(); i++){
                            String installation = jsonInstallations.getString(i);
                            installations.add(installation.split(": ")[1]);
                        }
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
