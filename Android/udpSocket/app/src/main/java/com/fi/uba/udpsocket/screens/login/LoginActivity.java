package com.fi.uba.udpsocket.screens.login;

import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.net.http.AndroidHttpClient;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.ActionBarActivity;
import android.util.Log;
import android.view.Menu;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
import android.widget.TextView;
import android.widget.Toast;

import com.fi.uba.udpsocket.R;
import com.fi.uba.udpsocket.domain.User;
import com.fi.uba.udpsocket.screens.installations.InstallationsActivity;

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


public class LoginActivity extends ActionBarActivity {

    public final static String USER_MESSAGE = "com.fi.uba.USER";

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
        getMenuInflater().inflate(R.menu.menu_login, menu);
        return false;
    }

    public void createAccount(View view) {
        String baseUrl = getResources().getString(R.string.tix_base_url);
        String createAccount = getResources().getString(R.string.tix_create_account_url);
        Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse(baseUrl + createAccount));
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
            // If the login is successful we show the create installation screen,

            Intent intent = new Intent(this, InstallationsActivity.class);
            intent.putExtra(USER_MESSAGE, user);
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_TASK_ON_HOME);
            startActivity(intent);
            this.finish();
        }
        else {
            CharSequence text = "The user or password is invalid.";
            int duration = Toast.LENGTH_SHORT;
            Toast toast = Toast.makeText(getApplicationContext(), text, duration);
            toast.show();
        }
    }

    private class LoginAsyncTask extends AsyncTask<String, Void, User> {

        AndroidHttpClient httpClient = AndroidHttpClient.newInstance("");

        public LoginAsyncTask(){
        }

        @Override
        protected User doInBackground(String... params) {
            Log.i(LoginAsyncTask.class.toString(), "Login for user: " + params[0]);

            String baseUrl = getResources().getString(R.string.tix_base_url);
            String loginUrl = getResources().getString(R.string.tix_login_account_url);
            String url = baseUrl + loginUrl + "?name=" + params[0] + "&password=" + params[1];

            HttpGet httpRequest = new HttpGet(url);
            JSONResponseHandler responseHandler = new JSONResponseHandler();
            User user = null;
            try {
                user = httpClient.execute(httpRequest, responseHandler);
            } catch (Exception e) {
                e.printStackTrace();
            } finally {
                if (httpClient != null)
                    httpClient.close();
            }

            if (user != null) {
                return new User(user.getId(), params[1], user.getInstallations());
            }
            else {
                return null;
            }
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
