package com.fi.uba.udpsocket;

import android.app.IntentService;

import android.content.Intent;

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
    private DatagramPacket packet;

    public UdpService() {
        super("UdpService");
    }

    public void init () {
        try {
            socket = new DatagramSocket();
            InetAddress local  = InetAddress.getByName(address);
            String messge = "";
            packet = new DatagramPacket(messge.getBytes(),0,local,port);
        } catch (SocketException e) {
            e.printStackTrace();
        } catch (UnknownHostException e) {
            e.printStackTrace();
        }
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        this.address = intent.getStringExtra("address");
        this.port = Integer.parseInt(intent.getStringExtra("port"));

        this.init();

        return super.onStartCommand(intent, flags, startId);
    }

    @Override
    protected void onHandleIntent(Intent intent) {
        try {
            Date currentDate = new Date();
            String message = currentDate.toString();


            int msg_lenght = message.length();
            byte []byteMessage = message.getBytes();

            packet.setData(byteMessage);
            packet.setLength(msg_lenght);

            //InetAddress local  = InetAddress.getByName(address);
            //DatagramPacket p = new DatagramPacket(byteMessage,msg_lenght,local,port);
            this.socket.send(packet);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
