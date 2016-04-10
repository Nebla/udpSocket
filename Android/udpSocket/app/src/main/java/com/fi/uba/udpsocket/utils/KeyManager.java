package com.fi.uba.udpsocket.utils;

/**
 * Created by adrian on 08/06/15.
 */

import android.app.Activity;
import android.content.Context;
import android.util.Base64;

import org.spongycastle.asn1.ASN1Encodable;
import org.spongycastle.asn1.ASN1Primitive;

import org.spongycastle.asn1.pkcs.PrivateKeyInfo;
import org.spongycastle.asn1.x509.SubjectPublicKeyInfo;
import org.spongycastle.util.io.pem.PemObject;
import org.spongycastle.util.io.pem.PemWriter;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.StringWriter;
import java.security.InvalidKeyException;
import java.security.KeyFactory;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.NoSuchAlgorithmException;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.Signature;
import java.security.SignatureException;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;

public class KeyManager extends Activity {

    Context context;

    public KeyManager(Context context){
        this.context = context;
    }

    /* Key generation */
    public void generateKeys(String alias) {

        try {
            KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA");
            kpg.initialize(2048);
            KeyPair keyPair = kpg.generateKeyPair();

            // Save the private key
            DataOutputStream out = new DataOutputStream(this.context.openFileOutput(alias, Context.MODE_PRIVATE));
            byte[] data = keyPair.getPrivate().getEncoded();
            out.write(data);
            out.close();

            // Save the public key
            String pubKeyFile = alias + ".pub";
            out = new DataOutputStream(this.context.openFileOutput(pubKeyFile, Context.MODE_PRIVATE));
            data = keyPair.getPublic().getEncoded();
            out.write(data);
            out.close();

        } catch (IOException e) {
            e.printStackTrace();
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        }
    }

    /* Public key */

    public PublicKey getPublicKey (String alias) {
        PublicKey pubKey = null;
        try {
            String pubKeyFile = alias + ".pub";
            DataInputStream in= new DataInputStream(this.context.openFileInput(pubKeyFile));
            byte[] data=new byte[in.available()];
            in.readFully(data);

            X509EncodedKeySpec keySpec = new X509EncodedKeySpec(data);
            KeyFactory kf = KeyFactory.getInstance("RSA");
            pubKey = kf.generatePublic(keySpec);
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (InvalidKeySpecException e) {
            e.printStackTrace();
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return pubKey;
    }

    public byte[] getPkcs1PublicKey(String alias) {
        PublicKey pub = this.getPublicKey(alias);
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

    public String getPemPublicKey (String alias) {
        /*PublicKey publicKey = this.getPublicKey(alias);
        byte[] publicKeyBytes = publicKey.getEncoded();

        PemObject pemObject = new PemObject("RSA PUBLIC KEY", publicKeyBytes);
        StringWriter stringWriter = new StringWriter();
        PemWriter pemWriter = new PemWriter(stringWriter);
        try {
            pemWriter.writeObject(pemObject);
            pemWriter.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

        String pemString = stringWriter.toString();
        return pemString;*/

        PemObject pemObject = new PemObject("RSA PUBLIC KEY", this.getPkcs1PublicKey(alias));
        StringWriter stringWriter = new StringWriter();
        PemWriter pemWriter = new PemWriter(stringWriter);
        try {
            pemWriter.writeObject(pemObject);
            pemWriter.close();

        } catch (IOException e) {
            e.printStackTrace();
        }
        return stringWriter.toString();
    }

    public String getBase64EncodedPemPublicKey (String alias) {
        String pemPublicKey = this.getPemPublicKey(alias);
        return Base64.encodeToString(pemPublicKey.getBytes(), Base64.NO_WRAP | Base64.NO_PADDING | Base64.URL_SAFE);
    }

    /* Private Key */
    public PrivateKey getPrivateKey (String alias) {
        PrivateKey privKey = null;
        DataInputStream in= null;
        try {
            in = new DataInputStream(this.context.openFileInput(alias));
            byte[] data = new byte[in.available()];
            in.readFully(data);

            PKCS8EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(data);
            KeyFactory kf = KeyFactory.getInstance("RSA");
            privKey = kf.generatePrivate(keySpec);
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (InvalidKeySpecException e) {
            e.printStackTrace();
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return privKey;
    }

    public byte[] getPkcs1PrivateKey(String alias) {
        PrivateKey priv = this.getPrivateKey(alias);

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

    public byte[] signMessageUsingSHA1(String keyAlias, String message) {
        Signature instance = null;
        byte []signed = new byte[0];
        try {
            instance = Signature.getInstance("SHA1withRSA");
            instance.initSign(this.getPrivateKey(keyAlias));
            instance.update(message.getBytes());
            signed = instance.sign();
        } catch (NoSuchAlgorithmException | InvalidKeyException | SignatureException e) {
            e.printStackTrace();
        }
        return signed;
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