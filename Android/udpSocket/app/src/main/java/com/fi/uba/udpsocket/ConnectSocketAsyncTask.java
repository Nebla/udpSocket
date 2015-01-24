package com.fi.uba.udpsocket;

import android.os.AsyncTask;
import android.os.Bundle;
import android.widget.TextView;

import org.w3c.dom.Text;

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
        int port = Integer.parseInt(params[1]);

        String message = params[2];

        try {
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
        }

        return message;
    }
}
