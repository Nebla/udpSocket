package com.fi.uba.udpsocket.screens.installations;

import android.app.ActivityManager;
import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.http.AndroidHttpClient;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.ActionBarActivity;
import android.util.Log;
import android.view.Menu;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import com.fi.uba.udpsocket.service.AlarmReceiver;
import com.fi.uba.udpsocket.R;
import com.fi.uba.udpsocket.domain.User;
import com.fi.uba.udpsocket.screens.login.LoginActivity;
import com.fi.uba.udpsocket.service.ServiceManager;
import com.fi.uba.udpsocket.utils.KeyManager;

import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.ResponseHandler;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.BasicResponseHandler;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.IOException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;


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
                //testKeys(newInstallationName);
            }
        }
    }

    public void testKeys (String newInstallationName) {
        EditText text = (EditText) findViewById(R.id.installation_name_text);
        String testString = text.getText().toString();

        KeyManager keyManager = new KeyManager(this.getApplicationContext());

        byte[] encryptedBytes = null;
        Cipher cipher = null;
        try {
            cipher = Cipher.getInstance("RSA");
            cipher.init(Cipher.ENCRYPT_MODE, keyManager.getPublicKey(newInstallationName));
            encryptedBytes = cipher.doFinal(testString.getBytes());
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        } catch (NoSuchPaddingException e) {
            e.printStackTrace();
        } catch (InvalidKeyException e) {
            e.printStackTrace();
        } catch (BadPaddingException e) {
            e.printStackTrace();
        } catch (IllegalBlockSizeException e) {
            e.printStackTrace();
        }

        byte[] result = new byte[0];
        Cipher decipher = null;
        try {
            decipher = Cipher.getInstance("RSA");
            decipher.init(Cipher.DECRYPT_MODE, keyManager.getPrivateKey(newInstallationName));
            result = decipher.doFinal(encryptedBytes);
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        } catch (NoSuchPaddingException e) {
            e.printStackTrace();
        } catch (InvalidKeyException e) {
            e.printStackTrace();
        } catch (BadPaddingException e) {
            e.printStackTrace();
        } catch (IllegalBlockSizeException e) {
            e.printStackTrace();
        }

        TextView resultTextView = (TextView) findViewById(R.id.test_result);

        String finalResult = "Encoded:\n"+new String(encryptedBytes) +
                            "\nDecoded:\n"+new String(result)+
                            "\nPublic Key:\n"+ keyManager.getPemPublicKey(newInstallationName) +
                            "\nEncoded public key:\n"+keyManager.getBase64EncodedPemPublicKey(newInstallationName);
        resultTextView.setText(finalResult);
    }

    private void showResult(String resultInstallationName) {

        EditText resultTextView = (EditText) findViewById(R.id.installation_name_text);
        String installationName = resultTextView.getText().toString();

        SharedPreferences.Editor editor = getSharedPreferences("InstallationPreferences", MODE_PRIVATE).edit();
        editor.putString("Installation", installationName);
        editor.apply();

        ServiceManager.startService(getApplicationContext(), installationName);
    }


    private void startService(View view) {
        EditText resultTextView = (EditText) findViewById(R.id.installation_name_text);
        String newInstallationName = resultTextView.getText().toString();

        Log.i("UdpActivity","Starting service");
        ServiceManager.startService(getApplicationContext(),newInstallationName);

    }

    public void stopService(View view) {
        Intent intent = new Intent(getApplicationContext(), AlarmReceiver.class);
        final PendingIntent pIntent = PendingIntent.getBroadcast(this, AlarmReceiver.REQUEST_CODE, intent, PendingIntent.FLAG_UPDATE_CURRENT);
        AlarmManager alarm = (AlarmManager) this.getSystemService(Context.ALARM_SERVICE);
        alarm.cancel(pIntent);

        /* Test generated file
        TextView textView = (TextView) findViewById(R.id.fileTest);
        StringBuilder builder = null;
        BufferedReader bufferedReader = null;
        try {
            bufferedReader = new BufferedReader(new FileReader(new
                    File(getFilesDir()+ File.separator+"saraza")));

            String read;
            builder = new StringBuilder("");
            while((read = bufferedReader.readLine()) != null){
                builder.append(read);
            }
            bufferedReader.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

        Log.d("Output", builder.toString());
        textView.setText(builder.toString());*/
    }

    private void showError(String errorMessage) {
        Context context = getApplicationContext();
        int duration = Toast.LENGTH_SHORT;
        Toast toast = Toast.makeText(context, errorMessage, duration);
        toast.show();
    }

    private void createNewInstallation(String newInstallationName) {

        KeyManager keyManager = new KeyManager(getApplicationContext());
        keyManager.generateKeys(newInstallationName);
        String encodedPublicKey = keyManager.getBase64EncodedPemPublicKey(newInstallationName);

        AsyncTask task = new CreateInstallationAsyncTask().execute(user.getId(), user.getPassword(), newInstallationName, encodedPublicKey);

    }


    private class CreateInstallationAsyncTask extends AsyncTask<String, Void, String> {

        AndroidHttpClient httpClient = AndroidHttpClient.newInstance("");

        public CreateInstallationAsyncTask(){
        }

        @Override
        protected String doInBackground(String... params) {
            Log.i(CreateInstallationAsyncTask.class.toString(), "Create new installation for user: " + params[0]);

            String userId = params[0];
            String userPassword = params[1];
            String installationName = params[2];
            String publicKey = params[3];

            String result = null;

            String baseUrl = getResources().getString(R.string.tix_base_url);
            String createUrl = getResources().getString(R.string.tix_create_installation_url);

            String url = baseUrl + createUrl;
            HttpPost httpPostRequest = new HttpPost(url);
            httpPostRequest.setHeader("Accept", "application/json");
            httpPostRequest.setHeader("content-type", "application/json");

            try {
                JSONObject object = new JSONObject();

                object.put("user_id", userId);
                object.put("password", userPassword);
                object.put("installation_name", installationName);
                object.put("encryption_key", publicKey);

                String postBody = object.toString();
                httpPostRequest.setEntity(new StringEntity(postBody, "UTF8"));
                JSONResponseHandler responseHandler = new JSONResponseHandler();
                result = httpClient.execute(httpPostRequest, responseHandler);
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

        @Override
        protected void onPostExecute(String installationName) {
            showResult(installationName);
        }

        private class JSONResponseHandler implements ResponseHandler<String> {

            private final String INSTALLATION_TAG = "installations";

            @Override
            public String handleResponse(HttpResponse response) throws ClientProtocolException, IOException {

                String installationName = null;

                // Server response
                String JSONResponse = new BasicResponseHandler().handleResponse(response);

                try {
                    /*{"id":50,"installations":"Installation: prueba4","name":"adrianmdu@gmail.com"}*/
                    JSONObject root = (JSONObject) new JSONTokener(JSONResponse).nextValue();

                    if (root.has(INSTALLATION_TAG)) {
                        installationName = root.getString(INSTALLATION_TAG);
                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                }

                return installationName;
            }
        }
    }
}
