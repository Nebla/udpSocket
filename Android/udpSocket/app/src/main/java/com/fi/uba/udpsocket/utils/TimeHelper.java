package com.fi.uba.udpsocket.utils;

import java.util.Calendar;
import java.util.Date;

/**
 * Created by adrian on 09/04/16.
 */
public class TimeHelper {

    public static String stringTimeStamp() {
        Calendar c = Calendar.getInstance();
        long now = c.getTimeInMillis();
        c.set(Calendar.HOUR_OF_DAY, 0);
        c.set(Calendar.MINUTE, 0);
        c.set(Calendar.SECOND, 0);
        c.set(Calendar.MILLISECOND, 0);
        long passed = (now - c.getTimeInMillis())*1000; // Server is prepared to receive microseconds

        return String.valueOf(passed);
    }

    public static float secondsSinceEpoch() {
        Calendar c = Calendar.getInstance();
        return c.getTimeInMillis()/1000;
    }

    public static Date currentDate() {
        return Calendar.getInstance().getTime();
    }
}
