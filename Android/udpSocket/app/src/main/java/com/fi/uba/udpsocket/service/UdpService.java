package com.fi.uba.udpsocket.service;

import android.app.AlarmManager;
import android.app.IntentService;

import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.util.Base64;
import android.util.Log;

import com.fi.uba.udpsocket.domain.PingStatus;
import com.fi.uba.udpsocket.service.AlarmReceiver;
import com.fi.uba.udpsocket.utils.KeyManager;
import com.fi.uba.udpsocket.utils.StringHelper;
import com.fi.uba.udpsocket.utils.TimeHelper;
import com.fi.uba.udpsocket.utils.TimeLogHelper;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;

/**
 * Created by adrian on 24/02/15.
 */
public class UdpService extends IntentService {

    // Constants
    private static final String logFileBase = "log";
    private static final int longMessageSize = 4400;

    public UdpService() {
        super("UdpService");
    }

    @Override
    protected void onHandleIntent(Intent intent) {

        Log.i("Udp Service", "Launched");

        // We need the installation name in the service to get the key pair
        String installationName = intent.getStringExtra("installation");
        //String address = intent.getStringExtra("address");
        //int port = intent.getIntExtra("port", 0);

        PingStatus.getInstance().updateValues();

        String address = "10.0.3.2";
        int port = 10001;

        // Create the communication channel
        DatagramSocket socket = createCommunicationChannel(address, port);
        if (socket == null) {
            return;
        }

        String _24hs = "86400000000";

        String t1 = TimeHelper.stringTimeStamp();
        String t2 = _24hs;
        String t3 = _24hs;
        String t4 = _24hs;

        String message;
        if (PingStatus.getInstance().shouldSendLongMessage()) {
            // Long message

            String lastFileName = PingStatus.getInstance().lastFileName();

            String longMessage = this.longMessage(installationName, lastFileName); //rellenoLargo(4400, check, str(told), logfile);
            message = t1 + "!!" + t2 + "!!" + t3 + "!!" + t4 + "!!" + longMessage;
            Log.i("Udp Service - Largo", "Size: "+String.valueOf(message.getBytes().length) + " Mensaje: " + message);

            // We check if we need to remove the log file because is already going to be sent in the next message
            if (PingStatus.getInstance().shouldSendSavedData()) {
                // The current data is being sent, so we need to delete lastFile
                String logFileName = logFileBase + "_" + lastFileName;
                Log.i("Udp Service", "Deleting log message: "+logFileName);
                TimeLogHelper.deleteFile(this.getApplicationContext(), logFileName);
            }
        } else {
            // Short message
            message = t1 + "!!" + t2 + "!!" + t3 + "!!" + t4;
            Log.i("Udp Service - Corto", "Size: "+String.valueOf(message.getBytes().length) + " Mensaje: " + message);
        }

        // Server response
        DatagramPacket packet = new DatagramPacket(message.getBytes(), message.getBytes().length);
        try {
            Log.d("UdpService", "Sending packet: " + message);
            socket.send(packet);
        } catch (IOException e) {
            e.printStackTrace();
            this.cancelOnError("IOException");
        }

        byte[] recievedMessage = new byte[8192];
        packet = new DatagramPacket(recievedMessage, recievedMessage.length);

        try {
            socket.receive(packet);
        } catch (IOException e) {
            e.printStackTrace();
        }

        String response = new String(packet.getData(), 0, packet.getLength());
        Log.i("Response", response);

        String[] separatedResponse = response.split("\\|");
        String data = separatedResponse[0] + "|" + separatedResponse[1] + "|" + separatedResponse[2] + "|" + TimeHelper.stringTimeStamp(); //#+ '|' + msg[4], en msg[4] queda el contenido del mensaje largo sin imprimir

        Integer payload = data.length();
        if (PingStatus.getInstance().shouldSendLongMessage()) {
            payload = (data + '|' + separatedResponse[4]).length();
        }

        Integer ipHeader = 20; // ip header length (min. 20 bytes)
        Integer udpHeader = 8; // udp header length (min. 8 bytes)
        String packetLength = String.valueOf(ipHeader + udpHeader + payload);

        String logFileName = logFileBase + "_" + PingStatus.getInstance().currentFileName();
        TimeLogHelper.logTimeMessage(this.getApplicationContext(), logFileName, "|" + packetLength + "|" + data);

        Log.i("Udp Service", "Finished");
    }

    private String longMessage(String installationName, String told) {
        String longMessage = StringHelper.randomString(longMessageSize);
        if (PingStatus.getInstance().shouldSendSavedData()) {
            // Content of the log message
            String logFileName = logFileBase + "_" + told;
            String fileMessage = TimeLogHelper.readLogTimeFile(this.getApplicationContext(), logFileName);

            // We need both the public and private keys generated during the installation
            KeyManager keyManager = new KeyManager(this.getApplicationContext());

            String PEMPublicKeyBase64Encoded = keyManager.getBase64EncodedPemPublicKey(installationName);

            byte[] sign = keyManager.signMessageUsingSHA1(installationName, fileMessage);
            String signBase64Encoded = Base64.encodeToString(sign, Base64.NO_WRAP);

            String messageBase64Encoded = Base64.encodeToString(fileMessage.getBytes(), Base64.NO_WRAP);


            /*Log.i("UdpService - Encoded public",PEMPublicKeyBase64Encoded);

            Log.i("UdpService - Sign",String.valueOf(sign));
            Log.i("UdpService - SignEncoded",signBase64Encoded);

            Log.i("UdpService - FileMessage",fileMessage);
            Log.i("UdpService - FileMessageEncoded",messageBase64Encoded);*/

            longMessage = "DATA;;" + PEMPublicKeyBase64Encoded + ";;" + signBase64Encoded + ";;" + logFileName + ";;" + messageBase64Encoded + ";;";

            // We complete the missing characters with random data
            if (longMessage.length() < longMessageSize) {
                String padding = StringHelper.randomString(longMessageSize - longMessage.length());
                longMessage = longMessage + padding;
            }
        }
        return longMessage;
    }

    // Communication channel: Creates an udp socket with the given address and port
    private DatagramSocket createCommunicationChannel(String address, int port) {
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
        }
        return socket;
    }

    private void cancelOnError(String errorMessage) {
        Log.e("UdpService", errorMessage);
        Intent intent = new Intent(getApplicationContext(), AlarmReceiver.class);
        final PendingIntent pIntent = PendingIntent.getBroadcast(this, AlarmReceiver.REQUEST_CODE, intent, PendingIntent.FLAG_UPDATE_CURRENT);
        AlarmManager alarm = (AlarmManager) this.getSystemService(Context.ALARM_SERVICE);
        alarm.cancel(pIntent);
    }
}
