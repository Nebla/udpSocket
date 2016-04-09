package com.fi.uba.udpsocket;

import android.app.AlarmManager;
import android.app.IntentService;

import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.util.Base64;
import android.util.Log;

import com.fi.uba.udpsocket.utils.KeyManager;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Random;

/**
 * Created by adrian on 24/02/15.
 */
public class UdpService extends IntentService {

    // Constants
    private static String logFileBase = "log";
    private static int longMessageSize = 44400;

    private static int numUniq = 0;
    private static boolean checker = false;

    public UdpService() {
        super("UdpService");
    }

    @Override
    protected void onHandleIntent(Intent intent) {

        // We need the installation name in the service to get the key pair
        String installationName = intent.getStringExtra("installation");

        String address = intent.getStringExtra("address");
        int port = intent.getIntExtra("port", 0);

        //TODO: Check the appropiate value for the log file told, t0_filename and t0
        String told = "LOG_FILE_NAME";

        // Create the communication channel
        DatagramSocket socket = null;
        try {
            socket = new DatagramSocket();
            InetAddress ipAddress = InetAddress.getByName(address);
            socket.connect(ipAddress, port);
        }
        catch (SocketException e) {
            e.printStackTrace();
            this.cancelOnError("Socket creation socket exception");
        }
        catch (UnknownHostException e) {
            e.printStackTrace();
            this.cancelOnError("Socket connect unknown host error");
            return;
        }

        if (socket == null) {
            return;
        }

        String _24hs = "86400000000";

        String t1 = timeStamp();
        String t2 = _24hs;
        String t3 = _24hs;
        String t4 = _24hs;

        String message;

        if (numUniq == 0) {
            // Short message
            message = t1 + "!!" + t2 + "!!" + t3 + "!!" + t4;
            Log.i("Mensaje", "Mensaje Corto: " + message);
        } else {
            // Long message

            String longMessage = this.longMessage(installationName, told ); //rellenoLargo(4400, check, str(told), logfile);
            message = t1 + "!!" + t2 + "!!" + t3 + "!!" + t4 + "!!" + longMessage;
            Log.i("Mensaje", "Mensaje Largo: " + message);
        }

        // Server response
        DatagramPacket packet = new DatagramPacket(message.getBytes(), message.length());
        try {
            Log.d("UdpService", "Sending packet: " + message);
            socket.send(packet);
        } catch (IOException e) {
            e.printStackTrace();
            this.cancelOnError("IOException");
        }

        byte[] lMsg = new byte[8192];
        DatagramPacket dp = new DatagramPacket(lMsg, lMsg.length);

        try {
            socket.receive(dp);
        } catch (IOException e) {
            e.printStackTrace();
        }

        String response = new String(dp.getData(), 0, dp.getLength());
        Log.i("Response", response);

        String[] separatedResponse = response.split("\\|");
        String data = separatedResponse[0] + "|" + separatedResponse[1] + "|" + separatedResponse[2] + "|" + timeStamp(); //#+ '|' + msg[4], en msg[4] queda el contenido del mensaje largo sin imprimir

        Integer payload = data.length();
        if (numUniq % 2 != 0) {
            payload = (data + '|' + separatedResponse[4]).length();
        }

        Integer ipHeader = 20; // ip header length (min. 20 bytes)
        Integer udpHeader = 8; // udp header length (min. 8 bytes)
        String packetLength = String.valueOf(ipHeader + udpHeader + payload);

        String logFileName = logFileBase + "_" + told;
        logMessage(logFileName, "|" + packetLength + "|" + data);

        numUniq = (numUniq+1)%2;
    }

    private String timeStamp() {
        Calendar c = Calendar.getInstance();
        long now = c.getTimeInMillis();
        c.set(Calendar.HOUR_OF_DAY, 0);
        c.set(Calendar.MINUTE, 0);
        c.set(Calendar.SECOND, 0);
        c.set(Calendar.MILLISECOND, 0);
        long passed = now - c.getTimeInMillis();

        return String.valueOf(passed);
    }

    private void logMessage(String fileName, String message) {

        SimpleDateFormat sdf = new SimpleDateFormat("dd/MM/yyyy|k:m:s,S");
        String currentDateandTime = sdf.format(new Date());

        String log = currentDateandTime + " " + message;

        try {
            BufferedWriter bufferedWriter = new BufferedWriter(new FileWriter(new
                    File(getFilesDir()+File.separator+fileName),true));
            bufferedWriter.write(log);
            bufferedWriter.close();
        }
        catch (IOException e) {
            Log.e("UdpService",e.getMessage());
            e.printStackTrace();
        }

    }

    private String longMessage(String installationName, String told) {
        String longMessage = this.randomString(longMessageSize);
        if (checker) {
            // Open log message
            String logFileName = logFileBase + "_" + told;
            StringBuilder builder = new StringBuilder("");
            BufferedReader bufferedReader = null;
            try {
                bufferedReader = new BufferedReader(new FileReader(new
                        File(getFilesDir()+ File.separator+logFileName)));

                String read;
                while((read = bufferedReader.readLine()) != null){
                    builder.append(read);
                }
                bufferedReader.close();
            } catch (IOException e) {
                e.printStackTrace();
            }

            // Content of the log message
            String fileMessage = builder.toString();

            // We need both the public and private keys generated during the installation
            KeyManager keyManager = new KeyManager(this.getApplicationContext());

            String PEMPublicKeyBase64Encoded = keyManager.getBase64EncodedPemPublicKey(installationName);

            byte[] sign = keyManager.signMessageUsingSHA1(installationName, fileMessage);
            String signBase64Encoded = Base64.encodeToString(sign, Base64.NO_WRAP | Base64.NO_PADDING | Base64.URL_SAFE);

            String messageBase64Encoded = Base64.encodeToString(fileMessage.getBytes(), Base64.NO_WRAP | Base64.NO_PADDING | Base64.URL_SAFE);

            longMessage = "DATA;;" + PEMPublicKeyBase64Encoded + ";;" + signBase64Encoded + ";;" + logFileName + ";;" + messageBase64Encoded + ";;";

            // We complete the missing characters with random data
            if (longMessage.length() < longMessageSize) {
                String padding = this.randomString(longMessageSize - longMessage.length());
                longMessage = longMessage + padding;
            }
        }
        return longMessage;
    }

    private String randomString(int size) {
        Random generator = new Random();
        StringBuilder randomStringBuilder = new StringBuilder();

        int tempChar;
        for (int i = 0; i < size; i++){
            tempChar = (generator.nextInt(10));
            randomStringBuilder.append(tempChar);
        }
        return randomStringBuilder.toString();
    }

    private void cancelOnError(String errorMessage) {
        Log.e("UdpService", errorMessage);
        Intent intent = new Intent(getApplicationContext(), AlarmReceiver.class);
        final PendingIntent pIntent = PendingIntent.getBroadcast(this, AlarmReceiver.REQUEST_CODE, intent, PendingIntent.FLAG_UPDATE_CURRENT);
        AlarmManager alarm = (AlarmManager) this.getSystemService(Context.ALARM_SERVICE);
        alarm.cancel(pIntent);
    }
}
