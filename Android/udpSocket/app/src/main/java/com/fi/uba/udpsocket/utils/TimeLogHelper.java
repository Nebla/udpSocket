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

    public static String readLogTimeFile(String fileName) {
        StringBuilder builder = new StringBuilder("");
        BufferedReader bufferedReader = null;
        try {
            String filePath = Environment.getDataDirectory().getAbsolutePath() + File.separator + fileName;
            bufferedReader = new BufferedReader(new FileReader(new File(filePath)));

            String read;
            while ((read = bufferedReader.readLine()) != null) {
                builder.append(read);
            }
            bufferedReader.close();
        } catch (IOException e) {
            Log.e("TimeLogHelper - read", e.getMessage());
            e.printStackTrace();
        }
        return builder.toString();
    }

    public static void logTimeMessage(String fileName, String message) {

        SimpleDateFormat sdf = new SimpleDateFormat("dd/MM/yyyy|k:m:s,S");
        String currentDateandTime = sdf.format(new Date());

        String log = currentDateandTime + " " + message;

        try {
            String filePath = Environment.getDataDirectory().getAbsolutePath() + File.separator + fileName;
            BufferedWriter bufferedWriter = new BufferedWriter(new FileWriter(new File(filePath),true));

            bufferedWriter.write(log);
            bufferedWriter.close();
        }
        catch (IOException e) {
            Log.e("TimeLogHelper - log", e.getMessage());
            e.printStackTrace();
        }
    }

    public static boolean deleteFile(String fileName) {
        File logFile = new File(Environment.getDataDirectory()+File.separator+fileName);
        return logFile.delete();
    }
}
