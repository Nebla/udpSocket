package com.fi.uba.udpsocket.domain;

import java.util.Date;

/**
 * Created by adrian on 09/04/16.
 */
public class PingStatus {

    private static final Object lock = new Object();
    private static volatile PingStatus instance;

    private static int numUniq;
    private static boolean checker;

    /*private static String t0;
    private static String t0Filename;
    private static Date t0Date;
    private static String tOldFilename;*/

    private PingStatus () {
        numUniq = 0;
        checker = false;


    }

    public static PingStatus getInstance() {
        PingStatus status = instance;
        if (status == null) {
            synchronized (lock) {    // While we were waiting for the lock, another
                status = instance;        // thread may have instantiated the object.
                if (status == null) {
                    status = new PingStatus();
                    instance = status;
                }
            }
        }
        return status;
    }

    public int getNumUniq() {
        return numUniq;
    }

    public boolean shouldSendData () {
        return checker;
    }

    public void updateValues () {
        numUniq = (numUniq + 1)%2;
    }
}
