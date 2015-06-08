package com.fi.uba.udpsocket.domain;

import android.os.Parcel;
import android.os.Parcelable;

import java.util.ArrayList;

/**
 * Created by adrian on 07/06/15.
 */
public class User implements Parcelable {

    private String id;
    private ArrayList<String> installations;

    public User(String id, ArrayList<String> installations) {
        this.id = id;
        this.installations = installations;
    }

    private User(Parcel in) {
        id = in.readString();
        installations = new ArrayList<>();
        in.readStringList(installations);
    }

    public String getId() {
        return this.id;
    }

    public ArrayList<String> getInstallations() {
        return this.installations;
    }

    /* This is used to regenerate the object.
     * All Parcelables must have a CREATOR that implements these two methods
     */
    public static final Parcelable.Creator<User> CREATOR = new Parcelable.Creator<User>() {
        public User createFromParcel(Parcel in) {
            return new User(in);
        }
        public User[] newArray(int size) {
            return new User[size];
        }
    };

    @Override
    public int describeContents() {
        return 0;
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeString(this.getId());
        dest.writeStringList(this.getInstallations());
    }
}

