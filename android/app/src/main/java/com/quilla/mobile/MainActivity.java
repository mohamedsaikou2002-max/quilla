package com.quilla.mobile;
import android.app.Activity;
import android.os.Bundle;
import android.content.Context;
import android.graphics.Color;
import android.webkit.*;
import android.widget.*;
import android.text.InputType;
import android.util.Base64;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import java.security.KeyStore;
import java.net.URI;
import javax.crypto.*;
import javax.crypto.spec.GCMParameterSpec;

public class MainActivity extends Activity {
  private static final String KEY = "quilla_pair_token";
  private String host="",token="";
  private WebView web;
  private android.content.SharedPreferences prefs(){return getSharedPreferences("quilla",Context.MODE_PRIVATE);}
  @Override public void onCreate(Bundle b){super.onCreate(b);
    host=prefs().getString("host","");
    token=decrypt(prefs().getString("token",""));
    if(host.isEmpty()||token.isEmpty())config();else open();
  }
  private SecretKey secretKey() throws Exception {
    KeyStore ks=KeyStore.getInstance("AndroidKeyStore");ks.load(null);
    if(!ks.containsAlias(KEY)){
      KeyGenerator gen=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");
      gen.init(new KeyGenParameterSpec.Builder(KEY,KeyProperties.PURPOSE_ENCRYPT|KeyProperties.PURPOSE_DECRYPT)
        .setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).build());
      gen.generateKey();
    }
    return (SecretKey)ks.getKey(KEY,null);
  }
  private String encrypt(String text){try{
    Cipher c=Cipher.getInstance("AES/GCM/NoPadding");c.init(Cipher.ENCRYPT_MODE,secretKey());
    byte[] nonce=c.getIV(),data=c.doFinal(text.getBytes("UTF-8")),out=new byte[nonce.length+data.length];
    System.arraycopy(nonce,0,out,0,nonce.length);System.arraycopy(data,0,out,nonce.length,data.length);
    return Base64.encodeToString(out,Base64.NO_WRAP);
  }catch(Exception e){return "";}}
  private String decrypt(String cipher){try{
    byte[] all=Base64.decode(cipher,Base64.NO_WRAP);if(all.length<29)return "";
    byte[] iv=new byte[12],data=new byte[all.length-12];
    System.arraycopy(all,0,iv,0,12);System.arraycopy(all,12,data,0,data.length);
    Cipher c=Cipher.getInstance("AES/GCM/NoPadding");c.init(Cipher.DECRYPT_MODE,secretKey(),new GCMParameterSpec(128,iv));
    return new String(c.doFinal(data),"UTF-8");
  }catch(Exception e){return "";}}
  private boolean valid(String s){try{
    if(!s.matches("[0-9.]+:[0-9]{2,5}"))return false;
    String[] p=s.split(":");int port=Integer.parseInt(p[1]);if(port<1024||port>65535)return false;
    String[] v=p[0].split("\\.");if(v.length!=4)return false;
    int[] a=new int[4];for(int i=0;i<4;i++){a[i]=Integer.parseInt(v[i]);if(a[i]<0||a[i]>255)return false;}
    return a[0]==10||(a[0]==172&&a[1]>=16&&a[1]<=31)||(a[0]==192&&a[1]==168)||(a[0]==100&&a[1]>=64&&a[1]<=127);
  }catch(Exception e){return false;}}
  private boolean permitted(String target){try{
    URI u=new URI(target);String p=u.getPath();
    return "http".equals(u.getScheme())&&host.equals(u.getRawAuthority())
      &&(p.equals("/")||p.equals("/chat")||p.equals("/styles.css")||p.equals("/style.css")||p.startsWith("/static/"));
  }catch(Exception e){return false;}}
  private void config(){
    if(web!=null){web.removeJavascriptInterface("QuillaAndroid");web.destroy();web=null;}
    LinearLayout layout=new LinearLayout(this);layout.setOrientation(1);layout.setPadding(35,65,35,25);layout.setBackgroundColor(Color.rgb(16,13,10));
    TextView title=new TextView(this);title.setText("QUILLA • LOCAL AI");title.setTextSize(26);title.setTextColor(Color.rgb(227,184,120));layout.addView(title);
    TextView note=new TextView(this);note.setText("Connect your phone and laptop to trusted private Wi-Fi. Start your laptop host, then enter its IPv4 address and pairing token.");
    note.setTextColor(Color.LTGRAY);note.setPadding(0,30,0,15);layout.addView(note);
    EditText address=new EditText(this);address.setHint("192.168.1.25:5000");address.setText(host);address.setTextColor(-1);address.setHintTextColor(Color.GRAY);address.setSingleLine(true);layout.addView(address);
    EditText password=new EditText(this);password.setHint("Pairing token");password.setText(token);password.setTextColor(-1);password.setHintTextColor(Color.GRAY);password.setSingleLine(true);
    password.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_PASSWORD);layout.addView(password);
    TextView error=new TextView(this);error.setTextColor(Color.rgb(252,150,110));layout.addView(error);
    Button connect=new Button(this);connect.setText("CONNECT TO LAPTOP");layout.addView(connect);
    connect.setOnClickListener(v->{
      String addr=address.getText().toString().trim(),key=password.getText().toString().trim();
      if(!valid(addr)||key.length()<24){error.setText("Enter a private IPv4:port and a valid 24+ character token.");return;}
      host=addr;token=key;prefs().edit().putString("host",host).putString("token",encrypt(token)).apply();open();
    });
    setContentView(layout);
  }
  private void open(){
    LinearLayout layout=new LinearLayout(this);layout.setOrientation(1);
    LinearLayout bar=new LinearLayout(this);
    Button settings=new Button(this);settings.setText("⚙ CONNECTION");settings.setOnClickListener(v->config());bar.addView(settings);
    Button reload=new Button(this);reload.setText("↻ RELOAD");reload.setOnClickListener(v->{if(web!=null)web.reload();});bar.addView(reload);
    layout.addView(bar);
    web=new WebView(this);WebSettings w=web.getSettings();w.setJavaScriptEnabled(true);w.setDomStorageEnabled(true);w.setAllowContentAccess(false);w.setAllowFileAccess(false);
    w.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);w.setSupportMultipleWindows(false);w.setJavaScriptCanOpenWindowsAutomatically(false);
    CookieManager.getInstance().setAcceptThirdPartyCookies(web,false);
    web.addJavascriptInterface(new Object(){@JavascriptInterface public String deviceToken(){return token;}},"QuillaAndroid");
    web.setWebViewClient(new WebViewClient(){
      @Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest r){return !permitted(r.getUrl().toString());}
      @Override public void onReceivedError(WebView view,WebResourceRequest r,WebResourceError e){
        if(r.isForMainFrame())Toast.makeText(MainActivity.this,"Host unreachable. Check Wi-Fi, laptop IP and firewall.",Toast.LENGTH_LONG).show();
      }
    });
    layout.addView(web,new LinearLayout.LayoutParams(-1,0,1));setContentView(layout);
    web.loadUrl("http://"+host+"/chat");
  }
  @Override public void onBackPressed(){if(web!=null&&web.canGoBack())web.goBack();else config();}
}
