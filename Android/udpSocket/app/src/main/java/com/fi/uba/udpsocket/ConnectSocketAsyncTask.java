package com.fi.uba.udpsocket;

import android.os.AsyncTask;
import android.util.Log;

import java.io.Console;
import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;

/**
 * Created by adrian on 24/01/15.
 */
public class ConnectSocketAsyncTask extends AsyncTask <String, Void, String> {


    public ConnectSocketAsyncTask() {

    }

    @Override
    protected String doInBackground(String... params) {

        String address = params[0];
        String message = params[2];

        try {
            int port = Integer.parseInt(params[1]);
            DatagramSocket s = new DatagramSocket();
            InetAddress local  = InetAddress.getByName(address);
            int msg_lenght = message.length();
            byte []byteMessage = message.getBytes();
            DatagramPacket p = new DatagramPacket(byteMessage,msg_lenght,local,port);
            s.send(p);
        } catch (SocketException e) {
            e.printStackTrace();
        } catch (UnknownHostException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (NumberFormatException e) {
            Log.e("ConnectSocketAsyncTask", "Invalid port entered");
        }

        return message;
    }
}
