package com.fi.uba.udpsocket.domain;

import android.util.Log;

import com.fi.uba.udpsocket.utils.TimeHelper;

import java.util.Date;

/**
 * Created by adrian on 09/04/16.
 */
public class PingStatus {

    private static final Object lock = new Object();
    private static volatile PingStatus instance;

    private boolean longMessage;
    private boolean sendAllData;

    private String lastFileName;
    private Date currentDate;
    private String currentFilename;

    private PingStatus () {
        longMessage = true; // It should init in true, because the first thing we do is updating all the values
        sendAllData = false;

        currentDate = TimeHelper.currentDate();
        currentFilename = String.valueOf(currentDate.getTime());
        lastFileName = "";
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

    public boolean shouldSendLongMessage() {
        return longMessage;
    }

    public boolean shouldSendSavedData () {
        return sendAllData;
    }

    public String lastFileName () {
        return lastFileName;
    }

    public String currentFileName () {
        return currentFilename;
    }

    public void updateValues () {
        longMessage = !longMessage;

        Date now = TimeHelper.currentDate();
        float difference = now.getTime() - currentDate.getTime();
        Log.i("Ping Statis", "Difference: "+String.valueOf(difference));
        if ((difference/1000 >= 60) && longMessage) {
            // We must check if the next is a long message, because in the other case, it could happen that a short message comes, and this values are reseted
            lastFileName = currentFilename;
            currentDate = now;
            currentFilename = String.valueOf(currentDate.getTime());
            sendAllData = true;
        }
        else {
            sendAllData = false;
        }
    }


}
