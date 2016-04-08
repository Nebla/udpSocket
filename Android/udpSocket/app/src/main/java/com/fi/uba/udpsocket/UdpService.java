package com.fi.uba.udpsocket;

import android.app.AlarmManager;
import android.app.IntentService;

import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
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

    private String address;
    private  int port;
    private DatagramSocket socket;

    public UdpService() {
        super("UdpService");
    }

    private void init () {
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
                InetAddress ipAddress = InetAddress.getByName(address);
                this.socket.connect(ipAddress, port);
            }
        } catch (UnknownHostException e) {
            e.printStackTrace();
            this.cancelOnError("Socket connect unknown host error");
            return;
        }

        Integer numUniq = intent.getIntExtra("numUniq", 0);

        String _24hs = "86400000000";

        String t1 = _24hs;
        String t2 = _24hs;
        String t3 = _24hs;
        String t4 = _24hs;


        //String message = currentDate.toString();

        //Long time= System.currentTimeMillis();
        //t1 = time.toString();
        //en_microsegundos=float(timestamp[0])*3600*(10**6)+float(timestamp[1])*60*(10**6)+float(timestamp[2])*(10**6)+float(timestamp[3])

        t1 = timeStamp();
        String message;

        if (numUniq == 0) {
            message = t1 + "!!" + t2 + "!!" + t3 + "!!" + t4;
            Log.i("Mensaje", "Mensaje Corto: " + message);
        } else {
            //file_tobe_deleted = logfile + str(told)
            String relleno_largo_msg = this.randomString(4400);//rellenoLargo(4400, check, str(told), logfile);
            message = t1 + "!!" + t2 + "!!" + t3 + "!!" + t4 + "!!" + relleno_largo_msg;
            //print("Mensaje Largo: " + message)
            //file_with_data = relleno_largo_msg.startswith('DATA;;')#Para luego borrar el archivo una vez enviado

            Log.i("Mensaje", "Mensaje Largo: " + message);
        }
        int msg_lenght = message.length();
        byte[] byteMessage = message.getBytes();

        //LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.nnnnnnnnn"));

        try {
            Log.d("UdpService", "Sending packet: " + message);
            DatagramPacket packet = new DatagramPacket(byteMessage, msg_lenght);
            this.socket.send(packet);
        } catch (IOException e) {
            e.printStackTrace();
            this.cancelOnError("IOException");
        } catch (Exception e) {
            e.printStackTrace();
            this.cancelOnError("Unknown error");
        }

        byte[] lMsg = new byte[8192];
        DatagramPacket dp = new DatagramPacket(lMsg, lMsg.length);


        try {
            this.socket.receive(dp);
        } catch (IOException e) {
            e.printStackTrace();
        }

        String response = new String(dp.getData(), 0, dp.getLength());
        Log.i("Response", response);


        String[] separatedResponse = response.split("|");


        //#print("after read 2")
        String data = separatedResponse[0] + "|" + separatedResponse[1] + "|" + separatedResponse[2] + "|" + timeStamp(); //#+ '|' + msg[4], en msg[4] queda el contenido del mensaje largo sin imprimir

        //#print("after read 3")
        //payload = 10
        Integer iph=20; //longitud ip header (min. 20 bytes)
        Integer udph=8; //longitud udp header (min. 8 bytes)

        Integer payload;

        if (numUniq % 2 == 0) {
            payload = data.length();
        }
        else {
            payload = (data + '|' + separatedResponse[4]).length();
        }

        String packetLength = String.valueOf(iph + udph + payload);
        logMessage("saraza", "|" + packetLength + "|" + data);

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

        SimpleDateFormat sdf = new SimpleDateFormat("d/MM/yyyy|k:m:s,S");
        String currentDateandTime = sdf.format(new Date());

        String log = currentDateandTime + " " + message;


        try {
            /*FileOutputStream fou = openFileOutput(fileName, MODE_APPEND);
            OutputStreamWriter outputStreamWriter = new OutputStreamWriter(fou);
            outputStreamWriter.write(log);
            outputStreamWriter.close();*/
            BufferedWriter bufferedWriter = new BufferedWriter(new FileWriter(new
                    File(getFilesDir()+File.separator+fileName)));
            bufferedWriter.write(log);
            bufferedWriter.close();
        }
        catch (IOException e) {
            Log.e("UdpService",e.getMessage());
            e.printStackTrace();
        }

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
