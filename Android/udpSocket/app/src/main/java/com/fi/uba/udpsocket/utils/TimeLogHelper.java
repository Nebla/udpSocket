package com.fi.uba.udpsocket.utils;

import java.text.SimpleDateFormat;
import java.io.InputStreamReader;
import java.io.FileOutputStream;
import java.io.FileInputStream;
import android.content.Context;
import java.io.BufferedReader;
import java.io.IOException;
import android.util.Log;
import java.util.Date;

/**
 * Created by adrian on 09/04/16.
 */
public class TimeLogHelper {

    public static String readLogTimeFile(Context context, String fileName) {

        StringBuilder builder = new StringBuilder("");
        try {
            FileInputStream inputStream = context.openFileInput(fileName);
            InputStreamReader isr = new InputStreamReader(inputStream);
            BufferedReader bufferedReader = new BufferedReader(isr);
            String line;
            while ((line = bufferedReader.readLine()) != null) {
                builder.append(line);
            }
        }
        catch (IOException e) {
            Log.e("TimeLogHelper - read", e.getMessage());
            e.printStackTrace();
        }
        return builder.toString();
    }

    public static void logTimeMessage(Context context, String fileName, String message) {

        FileOutputStream outputStream;

        SimpleDateFormat sdf = new SimpleDateFormat("dd/MM/yyyy|k:m:s,S");
        String currentDateandTime = sdf.format(new Date());

        String log = currentDateandTime + " " + message;

        try {
            outputStream = context.openFileOutput(fileName, Context.MODE_APPEND);
            outputStream.write(log.getBytes());
            outputStream.close();
        }
        catch (IOException e) {
            Log.e("TimeLogHelper - log", e.getMessage());
            e.printStackTrace();
        }
    }

    public static boolean deleteFile(Context context, String fileName) {
        return context.deleteFile(fileName);
    }
}
