package com.fi.uba.udpsocket.utils;

/**
 * Created by adrian on 08/06/15.
 */

import android.content.Context;
import android.util.Base64;
import android.util.Log;

import org.spongycastle.asn1.ASN1Encodable;
import org.spongycastle.asn1.ASN1Primitive;
import org.spongycastle.asn1.pkcs.PrivateKeyInfo;
import org.spongycastle.asn1.x509.SubjectPublicKeyInfo;
import org.spongycastle.util.io.pem.PemObject;
import org.spongycastle.util.io.pem.PemWriter;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.StringWriter;

import java.security.InvalidKeyException;
import java.security.KeyFactory;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.NoSuchAlgorithmException;
import java.security.NoSuchProviderException;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.Signature;
import java.security.SignatureException;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;

public class KeyManager {

    private KeyManager(){
    }

    /* Key generation */
    public static boolean generateKeys(Context context, String alias) {
        boolean success = true;
        DataOutputStream outputStream = null;
        try {
            KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA");
            kpg.initialize(512);
            KeyPair keyPair = kpg.generateKeyPair();

            // Save the private key
            outputStream = new DataOutputStream(context.openFileOutput(alias, Context.MODE_PRIVATE));
            byte[] data = keyPair.getPrivate().getEncoded();
            outputStream.write(data);

            // Save the public key
            String pubKeyFile = alias + ".pub";
            outputStream = new DataOutputStream(context.openFileOutput(pubKeyFile, Context.MODE_PRIVATE));
            data = keyPair.getPublic().getEncoded();
            outputStream.write(data);

        } catch (IOException | NoSuchAlgorithmException e) {
            e.printStackTrace();
            success = false;
        } finally {
            if (outputStream != null) {
                try {
                    outputStream.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }

            }
        }
        return success;
    }

    public static void removeKeys(Context context, String alias) {
        context.deleteFile(alias);
        String pubKeyFile = alias + ".pub";
        context.deleteFile(pubKeyFile);
    }

    /* Public key */
    public static PublicKey getPublicKey (Context context, String alias) {
        PublicKey publicKey = null;
        DataInputStream in = null;
        try {
            String pubKeyFile = alias + ".pub";
            in = new DataInputStream(context.openFileInput(pubKeyFile));
            byte[] data = new byte[in.available()];
            in.readFully(data);

            X509EncodedKeySpec keySpec = new X509EncodedKeySpec(data);
            KeyFactory kf = KeyFactory.getInstance("RSA");
            publicKey = kf.generatePublic(keySpec);


        } catch (InvalidKeySpecException | IOException | NoSuchAlgorithmException e) {
            e.printStackTrace();
        } finally {
            if (in != null) {
                try {
                    in.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }

        return publicKey;
    }

    public static byte[] getPkcs1PublicKey(Context context, String alias) {
        PublicKey pub = KeyManager.getPublicKey(context, alias);
        byte[] pubBytes = pub.getEncoded();

        SubjectPublicKeyInfo spkInfo = SubjectPublicKeyInfo.getInstance(pubBytes);
        ASN1Primitive primitive = null;
        byte[] publicKeyPKCS1 = new byte[0];
        try {
            primitive = spkInfo.parsePublicKey();
            publicKeyPKCS1 = primitive.getEncoded();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return publicKeyPKCS1;
    }

    public static String getPemPublicKey (Context context, String alias) {
        PemObject pemObject = new PemObject("RSA PUBLIC KEY", KeyManager.getPkcs1PublicKey(context, alias));
        StringWriter stringWriter = new StringWriter();
        PemWriter pemWriter = new PemWriter(stringWriter);
        try {
            pemWriter.writeObject(pemObject);
        } catch (IOException e) {
            e.printStackTrace();
        }
        finally {
            try {
                pemWriter.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        return stringWriter.toString();
    }

    public static String getBase64EncodedPemPublicKey (Context context, String alias) {
        String pemPublicKey = KeyManager.getPemPublicKey(context, alias);
        return Base64.encodeToString(pemPublicKey.getBytes(), Base64.NO_WRAP | Base64.NO_PADDING | Base64.URL_SAFE);
    }

    /* Private Key */
    public static PrivateKey getPrivateKey (Context context, String alias) {
        PrivateKey privKey = null;
        DataInputStream inputStream = null;
        try {
            inputStream = new DataInputStream(context.openFileInput(alias));
            byte[] data = new byte[inputStream.available()];
            inputStream.readFully(data);

            PKCS8EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(data);
            KeyFactory kf = KeyFactory.getInstance("RSA");
            privKey = kf.generatePrivate(keySpec);

        } catch (InvalidKeySpecException | IOException | NoSuchAlgorithmException e) {
            e.printStackTrace();
        } finally {
            if (inputStream != null) {
                try {
                    inputStream.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
        return privKey;
    }

    public static byte[] getPkcs1PrivateKey(Context context, String alias) {
        PrivateKey priv = KeyManager.getPrivateKey(context, alias);

        byte[] privBytes = priv.getEncoded();

        PrivateKeyInfo pkInfo = PrivateKeyInfo.getInstance(privBytes);
        ASN1Encodable encodable = null;
        byte[] privateKeyPKCS1 = new byte[0];
        try {
            encodable = pkInfo.parsePrivateKey();
            ASN1Primitive primitive = encodable.toASN1Primitive();
            privateKeyPKCS1 = primitive.getEncoded();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return privateKeyPKCS1;
    }

    /* Helper methods */

    public static byte[] signMessageUsingSHA1(Context context, String keyAlias, String message) {


        /*Provider[] providers = Security.getProviders();
        for (Provider provider : providers) {
            Log.i("CRYPTO","provider: "+provider.getName());
            Set<Provider.Service> services = provider.getServices();
            for (Provider.Service service : services) {
                Log.i("CRYPTO","  algorithm: "+service.getAlgorithm());
            }
        }*/

        byte []signed = new byte[0];
        try {
            Signature instance = Signature.getInstance("SHA1WithRSAEncryption","BC");
            instance.initSign(KeyManager.getPrivateKey(context, keyAlias));
            instance.update(message.getBytes());
            signed = instance.sign();

        } catch (NoSuchAlgorithmException | InvalidKeyException | SignatureException | NoSuchProviderException e) {
            e.printStackTrace();
        }

        Log.i("Key Manager - Sign", byteArray2Hex(signed));
        return signed;
    }

    /*private byte[] sign(byte[] bytes, String privateKey) throws Exception {
        Signature signature = Signature.getInstance("SHA256withRSA", "SC");
        signature.initSign(Crypto.getRSAPrivateKeyFromString(privateKey));
        signature.update(bytes);
        return signature.sign();
    }*/


    public static boolean verify(Context context, byte[] bytes, String keyAlias) {
        Boolean result = true;
        try {
            Signature signature = Signature.getInstance("SHA1WithRSAEncryption","BC");
            signature.initVerify(KeyManager.getPublicKey(context, keyAlias));
            result = signature.verify(bytes);
        } catch (NoSuchAlgorithmException | InvalidKeyException | SignatureException | NoSuchProviderException e) {
            e.printStackTrace();
        }
        return result;
    }

    private static final char[] hex = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'};
    private static String byteArray2Hex(byte[] bytes) {
        StringBuilder sb = new StringBuilder(bytes.length * 2);
        for (final byte b : bytes) {
            sb.append(hex[(b & 0xF0) >> 4]);
            sb.append(hex[b & 0x0F]);
        }
        return sb.toString();
    }

    /*public void generateKeys(){
        try {
            KeyPairGenerator generator;
            generator = KeyPairGenerator.getInstance("RSA", "BC");
            generator.initialize(256, new SecureRandom());
            KeyPair pair = generator.generateKeyPair();
            pubKey = pair.getPublic();
            privKey = pair.getPrivate();
            byte[] publicKeyBytes = pubKey.getEncoded();
            String pubKeyStr = new String(Base64.encode(publicKeyBytes, Base64.DEFAULT));
            byte[] privKeyBytes = privKey.getEncoded();
            String privKeyStr = new String(Base64.encode(privKeyBytes, Base64.DEFAULT));
            SPE = SP.edit();
            SPE.putString("PublicKey", pubKeyStr);
            SPE.putString("PrivateKey", privKeyStr);
            SPE.apply();
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        } catch (NoSuchProviderException e) {
            e.printStackTrace();
        }
    }
    public PublicKey getPublicKey(){
        String pubKeyStr = SP.getString("PublicKey", "");
        byte[] sigBytes = Base64.decode(pubKeyStr, Base64.DEFAULT);
        X509EncodedKeySpec x509KeySpec = new X509EncodedKeySpec(sigBytes);
        KeyFactory keyFact = null;
        try {
            keyFact = KeyFactory.getInstance("RSA", "BC");
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        } catch (NoSuchProviderException e) {
            e.printStackTrace();
        }

        try {
            return  keyFact.generatePublic(x509KeySpec);
        } catch (InvalidKeySpecException e) {
            e.printStackTrace();
        } catch (NullPointerException e) {
            e.printStackTrace();
        }
        return null;
    }
    public String getPublicKeyAsString(){
        return SP.getString("PublicKey", "");
    }
    public PrivateKey getPrivateKey(){
        String privKeyStr = SP.getString("PrivateKey", "");
        byte[] sigBytes = Base64.decode(privKeyStr, Base64.DEFAULT);
        X509EncodedKeySpec x509KeySpec = new X509EncodedKeySpec(sigBytes);
        KeyFactory keyFact = null;
        try {
            keyFact = KeyFactory.getInstance("RSA", "BC");
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        } catch (NoSuchProviderException e) {
            e.printStackTrace();
        }
        try {
            return  keyFact.generatePrivate(x509KeySpec);
        } catch (InvalidKeySpecException e) {
            e.printStackTrace();
        }
        return null;
    }
    public String getPrivateKeyAsString(){
        return SP.getString("PrivateKey", "");
    }*/
}


/*
public class AsymmetricAlgorithmRSA extends Activity {
    static final String TAG = "AsymmetricAlgorithmRSA";

    @Override
    public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    setContentView(R.layout.asym);

    // Original text
    String theTestText = "This is just a simple test!";
    TextView tvorig = (TextView)findViewById(R.id.tvorig);
    tvorig.setText("\n[ORIGINAL]:\n" + theTestText + "\n");

    // Generate key pair for 1024-bit RSA encryption and decryption
    Key publicKey = null;
    Key privateKey = null;
    try {
        KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA");
        kpg.initialize(1024);
        KeyPair kp = kpg.genKeyPair();
        publicKey = kp.getPublic();
        privateKey = kp.getPrivate();
    } catch (Exception e) {
        Log.e(TAG, "RSA key pair error");
    }

    // Encode the original data with RSA private key
    byte[] encodedBytes = null;
    try {
        Cipher c = Cipher.getInstance("RSA");
        c.init(Cipher.ENCRYPT_MODE, privateKey);
        encodedBytes = c.doFinal(theTestText.getBytes());
    } catch (Exception e) {
        Log.e(TAG, "RSA encryption error");
    }
    TextView tvencoded = (TextView)findViewById(R.id.tvencoded);
    tvencoded.setText("[ENCODED]:\n" +
        Base64.encodeToString(encodedBytes, Base64.DEFAULT) + "\n");

    // Decode the encoded data with RSA public key
    byte[] decodedBytes = null;
    try {
        Cipher c = Cipher.getInstance("RSA");
        c.init(Cipher.DECRYPT_MODE, publicKey);
        decodedBytes = c.doFinal(encodedBytes);
    } catch (Exception e) {
        Log.e(TAG, "RSA decryption error");
}
 */


/*
 KeyPair keyPair = null;
        try {
            KeyStore keyStore = KeyStore.getInstance(KeyStore.getDefaultType());
            keyStore.load(null);

            //String alias = this.keyIdentifier; // replace as required or get it as a function argument

            int nBefore = keyStore.size(); // debugging variable to help convince yourself this works

            //int nBefore = keyStore.size();
            if (!keyStore.containsAlias(alias)) {

                Calendar notBefore = Calendar.getInstance();
                Calendar notAfter = Calendar.getInstance();
                notAfter.add(Calendar.YEAR, 1);
                KeyPairGeneratorSpec spec = null;

                spec = new KeyPairGeneratorSpec.Builder(this)
                        .setAlias(alias)
                        .setKeyType("RSA")
                        .setKeySize(2048)
                        .setSubject(new X500Principal("CN=test"))
                        .setSerialNumber(BigInteger.ONE)
                        .setStartDate(notBefore.getTime())
                        .setEndDate(notAfter.getTime())
                        .build();

                KeyPairGenerator generator = KeyPairGenerator.getInstance("RSA", "AndroidKeyStore");
                generator.initialize(spec);

                keyPair = generator.generateKeyPair();

                this.savePublicKey(keyPair.getPublic(), alias);
                this.savePrivateKey(keyPair.getPrivate(), alias);

                int nAfter = keyStore.size();
                Log.v(KeyManager.class.getName(), "Before = " + nBefore + " After = " + nAfter);
            }
        }
        catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        } catch (NoSuchProviderException e) {
            e.printStackTrace();
        } catch (InvalidAlgorithmParameterException e) {
            e.printStackTrace();
        } catch (CertificateException e) {
            e.printStackTrace();
        } catch (KeyStoreException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return keyPair;
 */