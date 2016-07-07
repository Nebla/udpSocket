package com.fi.uba.udpsocket.utils;

import android.util.Log;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.logging.Logger;

/**
 * Created by adrian on 09/04/16.
 */
public class TimeHelper {

    private static final String logTag = TimeHelper.class.getSimpleName();

    private static long timeStampDate;
    private static long nanoTimeStamp = -1;

    private static void saveTimeStamp() {
        nanoTimeStamp = System.nanoTime();
        timeStampDate = Calendar.getInstance().getTimeInMillis();
    }

    private static long getNanoTime () {
        if (nanoTimeStamp == -1) {
            // We still don't have any timestamp
            TimeHelper.saveTimeStamp();
        }
        else {
            // We already have a timestamp, we should check if it is still valid (we are on the same day)
            SimpleDateFormat fmt = new SimpleDateFormat("yyyyMMdd");
            String currentDay = fmt.format(Calendar.getInstance().getTime());
            String timeStampDay = fmt.format(timeStampDate);
            if (! currentDay.equals(timeStampDay)) {
                // We are in a new day, we must take another timestamp
                TimeHelper.saveTimeStamp();
            }
        }

        /* We return the current nano timestamp (relative to an unknown date) minus the
         * miliseconds * 1000 since midnight
         */
        Calendar c = Calendar.getInstance();
        c.set(Calendar.HOUR_OF_DAY, 0);
        c.set(Calendar.MINUTE, 0);
        c.set(Calendar.SECOND, 0);
        c.set(Calendar.MILLISECOND, 0);
        long nanoSinceMidnight = (timeStampDate - c.getTimeInMillis())*1000000;

        return nanoTimeStamp - nanoSinceMidnight;
    }

    public static String stringTimeStamp() {
        /*Calendar c = Calendar.getInstance();
        long now = c.getTimeInMillis();

        c.set(Calendar.HOUR_OF_DAY, 0);
        c.set(Calendar.MINUTE, 0);
        c.set(Calendar.SECOND, 0);
        c.set(Calendar.MILLISECOND, 0);

        long passed = (now - c.getTimeInMillis())*1000;*/ // Server is prepared to receive microseconds

        long originalNanoTime = TimeHelper.getNanoTime();
        long currentNanoTime = System.nanoTime();

        Log.i(logTag, "Current: " + currentNanoTime);

        long nanoSinceMidnight = currentNanoTime - originalNanoTime;
        long microSeconds = nanoSinceMidnight/1000;
        Log.i(logTag, "Micro seconds: " + microSeconds);

        return String.valueOf(microSeconds);
    }

    public static float secondsSinceEpoch() {
        Calendar c = Calendar.getInstance();
        return c.getTimeInMillis()/1000;
    }

    public static Date currentDate() {
        return Calendar.getInstance().getTime();
    }
}
