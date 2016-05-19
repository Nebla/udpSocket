package com.fi.uba.udpsocket.utils;

import android.content.Context;
import android.content.SharedPreferences;

import com.fi.uba.udpsocket.R;

/**
 * Created by adrian on 4/18/16.
 */
public class PreferencesWrapper {

    public static void setInstallation(Context context, String installation) {
        PreferencesWrapper.setString(context,
                context.getString(R.string.preferences_name),
                context.getString(R.string.installation_key),
                installation);
    }

    public static String getInstallation(Context context) {
        return PreferencesWrapper.getString(context,
                context.getString(R.string.preferences_name),
                context.getString(R.string.installation_key));
    }

    public static void removeInstallation(Context context) {
        PreferencesWrapper.removeValue(context,
                context.getString(R.string.preferences_name),
                context.getString(R.string.installation_key));
    }

    public static void setString(Context context, String preferencesName, String key, String value) {
        SharedPreferences.Editor editor = context.getSharedPreferences(preferencesName, Context.MODE_PRIVATE).edit();
        editor.putString(key, value);
        editor.apply();
    }

    public static String getString(Context context, String preferencesName, String key) {
        SharedPreferences prefs = context.getSharedPreferences(preferencesName, Context.MODE_PRIVATE);
        return prefs.getString(key, null);

    }

    public static Integer increaseTimeoutCount(Context context) {
        Integer timeouts = getInteger(context,
                context.getString(R.string.preferences_name),
                context.getString(R.string.timeout_key));

        PreferencesWrapper.setInteger(context,
                context.getString(R.string.preferences_name),
                context.getString(R.string.timeout_key),
                timeouts+1);

        return timeouts + 1;
    }

    public static void removeTimeouts(Context context) {
        PreferencesWrapper.removeValue(context,
                context.getString(R.string.preferences_name),
                context.getString(R.string.timeout_key));
    }

    public static Integer increasePacketCount(Context context) {
        Integer packets = getInteger(context,
                context.getString(R.string.preferences_name),
                context.getString(R.string.packet_key));

        PreferencesWrapper.setInteger(context,
                context.getString(R.string.preferences_name),
                context.getString(R.string.packet_key),
                packets+1);

        return packets + 1;
    }

    public static void removePackets(Context context) {
        PreferencesWrapper.removeValue(context,
                context.getString(R.string.preferences_name),
                context.getString(R.string.packet_key));
    }

    public static void setInteger(Context context, String preferencesName, String key, Integer value) {
        SharedPreferences.Editor editor = context.getSharedPreferences(preferencesName, Context.MODE_PRIVATE).edit();
        editor.putInt(key, value);
        editor.apply();
    }

    public static Integer getInteger(Context context, String preferencesName, String key) {
        SharedPreferences prefs = context.getSharedPreferences(preferencesName, Context.MODE_PRIVATE);
        return prefs.getInt(key, 0);

    }

    public static void removeValue(Context context, String preferencesName, String key) {
        SharedPreferences.Editor editor = context.getSharedPreferences(preferencesName, Context.MODE_PRIVATE).edit();
        editor.remove(key);
        editor.apply();
    }


}
