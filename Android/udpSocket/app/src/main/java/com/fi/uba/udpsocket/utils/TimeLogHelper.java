package com.fi.uba.udpsocket.utils;

import android.os.Environment;
import android.util.Log;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * Created by adrian on 09/04/16.
 */
public class TimeLogHelper {

    public static String readLogTimeFile(String filename) {
        //String logFileName = logFileBase + "_" + told;
        StringBuilder builder = new StringBuilder("");
        BufferedReader bufferedReader = null;
        try {
            bufferedReader = new BufferedReader(new FileReader(new
                    File(Environment.getDataDirectory() + File.separator + filename)));

            String read;
            while ((read = bufferedReader.readLine()) != null) {
                builder.append(read);
            }
            bufferedReader.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return builder.toString();
    }

    public static void logTimeMessage(String fileName, String message) {

        SimpleDateFormat sdf = new SimpleDateFormat("dd/MM/yyyy|k:m:s,S");
        String currentDateandTime = sdf.format(new Date());

        String log = currentDateandTime + " " + message;

        try {
            BufferedWriter bufferedWriter = new BufferedWriter(new FileWriter(new
                    File(Environment.getDataDirectory()+File.separator+fileName),true));
            bufferedWriter.write(log);
            bufferedWriter.close();
        }
        catch (IOException e) {
            Log.e("UdpService", e.getMessage());
            e.printStackTrace();
        }
    }

    public static boolean deleteFile(String fileName) {
        File logFile = new File(Environment.getDataDirectory()+File.separator+fileName);
        return logFile.delete();
    }
}
