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

    public static void removeValue(Context context, String preferencesName, String key) {
        SharedPreferences.Editor editor = context.getSharedPreferences(preferencesName, Context.MODE_PRIVATE).edit();
        editor.remove(key);
        editor.apply();
    }


}
