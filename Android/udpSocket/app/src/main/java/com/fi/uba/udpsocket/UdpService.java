package com.fi.uba.udpsocket;

import android.app.AlarmManager;
import android.app.IntentService;

import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.util.Date;

/**
 * Created by adrian on 24/02/15.
 */
public class UdpService extends IntentService {

    private String address;
    private  int port;
    private DatagramSocket socket;

    public UdpService() {
        super("UdpService");
    }

    public void init () {
        try {
            this.socket = new DatagramSocket();
        } catch (SocketException e) {
            e.printStackTrace();
            this.cancelOnError("Socket creation socket exception");
        }
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        this.address = intent.getStringExtra("address");
        this.port = intent.getIntExtra("port", 0);

        this.init();

        return super.onStartCommand(intent, flags, startId);
    }

    @Override
    protected void onHandleIntent(Intent intent) {

        try {
            if (!this.socket.isConnected()) {
                InetAddress ipAddress  = InetAddress.getByName(address);
                this.socket.connect(ipAddress,port);
            }
        } catch (UnknownHostException e) {
            e.printStackTrace();
            this.cancelOnError("Socket connect unknown host error");
            return;
        }

        Date currentDate = new Date();
        String message = currentDate.toString();

        int msg_lenght = message.length();
        byte []byteMessage = message.getBytes();

        try {
            Log.d("UdpService", "Sending packet: "+message);
            DatagramPacket packet = new DatagramPacket(byteMessage, msg_lenght);
            this.socket.send(packet);
        } catch (IOException e) {
            e.printStackTrace();
            this.cancelOnError("IOException");
        } catch (Exception e) {
            e.printStackTrace();
            this.cancelOnError("Unknown error");
        }
    }

    private void cancelOnError(String errorMessage) {
        Log.e("UdpService", errorMessage);
        Intent intent = new Intent(getApplicationContext(), AlarmReceiver.class);
        final PendingIntent pIntent = PendingIntent.getBroadcast(this, AlarmReceiver.REQUEST_CODE, intent, PendingIntent.FLAG_UPDATE_CURRENT);
        AlarmManager alarm = (AlarmManager) this.getSystemService(Context.ALARM_SERVICE);
        alarm.cancel(pIntent);
    }
}
