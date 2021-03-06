package com.fi.uba.udpsocket.utils;

import java.io.File;
import java.text.SimpleDateFormat;
import java.io.InputStreamReader;
import java.io.FileOutputStream;
import java.io.FileInputStream;
import android.content.Context;
import java.io.BufferedReader;
import java.io.IOException;
import android.util.Log;
import java.util.Date;
import java.util.Locale;

/**
 * Created by adrian on 09/04/16.
 */
public class TimeLogHelper {

    private static final String logTag = TimeLogHelper.class.getSimpleName();
    public static final String logFileBase = "log";

    public static String readLogTimeFile(Context context, String fileName) {
        FileInputStream inputStream = null;
        StringBuilder builder = new StringBuilder("");
        try {
            inputStream = context.openFileInput(fileName);
            InputStreamReader isr = new InputStreamReader(inputStream);
            BufferedReader bufferedReader = new BufferedReader(isr);
            String line;
            while ((line = bufferedReader.readLine()) != null) {
                builder.append(line);
                builder.append(System.getProperty("line.separator"));
            }
        }
        catch (IOException e) {
            Log.e(logTag, "Read Error:" + e.getMessage());
            e.printStackTrace();
        }
        finally {
            if (inputStream != null) {
                try {
                    inputStream.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
        String result = builder.toString();
        //Log.i("Time Log - Read:",result);
        return result;
    }

    public static void logTimeMessage(Context context, String fileName, String message) {

        FileOutputStream outputStream = null;

        SimpleDateFormat sdf = new SimpleDateFormat("MM/dd/yy|kk:mm:ss,S000", Locale.getDefault());
        String currentDateandTime = sdf.format(new Date());

        String log = currentDateandTime + " " + message + "\n";

        Log.i(logTag, "Log Message: "+log);
        try {
            outputStream = context.openFileOutput(fileName, Context.MODE_APPEND);
            outputStream.write(log.getBytes());
        }
        catch (IOException e) {
            Log.e(logTag, "Log Error: "+ e.getMessage());
            e.printStackTrace();
        }
        finally {
            if (outputStream != null) {
                try {
                    outputStream.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    public static boolean deleteFile(Context context, String fileName) {
        return context.deleteFile(fileName);
    }

    public static void deleteAllFiles(Context context) {

        String directory = context.getApplicationInfo().dataDir;

        for(File f: context.getFilesDir().listFiles()) {
            if (f.getName().startsWith(logFileBase))
                context.deleteFile(f.getName());
        }
    }
}
