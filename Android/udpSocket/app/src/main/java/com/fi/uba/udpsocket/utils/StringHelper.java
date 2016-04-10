package com.fi.uba.udpsocket.utils;

import java.util.Random;

/**
 * Created by adrian on 09/04/16.
 */
public class StringHelper {

    public static String randomString(int size) {
        Random generator = new Random();
        StringBuilder randomStringBuilder = new StringBuilder();

        int tempChar;
        for (int i = 0; i < size; i++){
            tempChar = (generator.nextInt(10));
            randomStringBuilder.append(tempChar);
        }
        return randomStringBuilder.toString();
    }
}
