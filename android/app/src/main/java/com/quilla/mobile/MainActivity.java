package com.quilla.mobile;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.content.SharedPreferences;
import android.net.Uri;
import android.graphics.Color;
import android.view.Window;
import org.json.JSONObject;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.InetAddress;
import java.net.URI;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends Activity {
    private WebView web;
    private ExecutorService executor;
    private SharedPreferences prefs;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(Color.rgb(6, 10, 10));
        getWindow().setNavigationBarColor(Color.rgb(6, 10, 10));
        getWindow().getDecorView().setSystemUiVisibility(0);
        prefs = getSharedPreferences("quilla_config", MODE_PRIVATE);
        executor = Executors.newSingleThreadExecutor();
        web = new WebView(this);
        web.setBackgroundColor(Color.rgb(6, 10, 10));
        web.getSettings().setJavaScriptEnabled(true);
        web.getSettings().setDomStorageEnabled(false);
        web.getSettings().setAllowContentAccess(false);
        web.getSettings().setAllowFileAccess(true);
        web.getSettings().setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        web.getSettings().setJavaScriptCanOpenWindowsAutomatically(false);
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
                Uri url = req.getUrl();
                return !"file".equals(url.getScheme()) || !url.getPath().startsWith("/android_asset/");
            }
        });
        web.addJavascriptInterface(new Bridge(), "QuillaNative");
        setContentView(web);
        web.loadUrl("file:///android_asset/index.html");
    }

    private void callback(String method, String json) {
        runOnUiThread(() -> {
            if (web != null) web.evaluateJavascript("window.QUILLA."+method+"("+JSONObject.quote(json)+")", null);
        });
    }

    private static boolean permittedUrl(String candidate) {
        try {
            URI uri = new URI(candidate);
            if (!uri.isAbsolute() || uri.getUserInfo() != null || uri.getQuery() != null || uri.getFragment() != null) return false;
            String host = uri.getHost();
            if (host == null || host.isEmpty()) return false;
            if ("https".equalsIgnoreCase(uri.getScheme())) return true;
            if (!"http".equalsIgnoreCase(uri.getScheme())) return false;
            // HTTP only for explicitly local IPv4 or tailnet addresses, on trusted networks.
            if (!host.matches("\\d+\\.\\d+\\.\\d+\\.\\d+")) return false;
            String[] nums = host.split("\\.");
            int[] octets = new int[4];
            for (int i=0;i<4;i++) {
                octets[i] = Integer.parseInt(nums[i]);
                if (octets[i]<0 || octets[i]>255) return false;
            }
            return octets[0] == 10 || (octets[0]==192 && octets[1]==168)
                || (octets[0]==172 && octets[1]>=16 && octets[1]<=31)
                || (octets[0]==100 && octets[1]>=64 && octets[1]<=127);
        } catch (Exception ignored) { return false; }
    }

    private String request(String method, String path, String body) throws Exception {
        String base = prefs.getString("endpoint", "");
        String token = prefs.getString("token", "");
        if (!permittedUrl(base) || token.length() < 32) throw new Exception("Configure laptop address and a 32+ character pairing token.");
        HttpURLConnection conn = (HttpURLConnection)new URL(base + path).openConnection();
        try {
            conn.setRequestMethod(method);
            conn.setConnectTimeout(6000);
            conn.setReadTimeout(path.equals("/api/chat") ? 125000 : 7000);
            conn.setRequestProperty("Authorization", "Bearer " + token);
            conn.setRequestProperty("Accept", "application/json");
            conn.setRequestProperty("Cache-Control", "no-store");
            conn.setInstanceFollowRedirects(false);
            if (body != null) {
                byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
                if(bytes.length>65536) throw new Exception("Message payload exceeds 64 KB.");
                conn.setRequestProperty("Content-Type", "application/json");
                conn.setDoOutput(true);
                try(OutputStream out = conn.getOutputStream()) { out.write(bytes); }
            }
            int status = conn.getResponseCode();
            InputStream stream = status >= 400 ? conn.getErrorStream() : conn.getInputStream();
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            if (stream != null) try(InputStream in = stream) {
                byte[] buf = new byte[4096]; int length;
                while((length=in.read(buf))!=-1) {
                    if(bytes.size()+length>262144) throw new Exception("Unexpectedly large server response.");
                    bytes.write(buf,0,length);
                }
            }
            String response = bytes.toString(StandardCharsets.UTF_8.name());
            if(status<200 || status>=300) {
                String msg="Server returned HTTP " + status;
                try { msg = new JSONObject(response).optString("error", msg); } catch(Exception ignored){}
                throw new Exception(msg);
            }
            return response;
        } finally { conn.disconnect(); }
    }

    final class Bridge {
        @JavascriptInterface public String settings() {
            JSONObject json = new JSONObject();
            try {
                json.put("endpoint", prefs.getString("endpoint", ""));
                json.put("paired", prefs.getString("token", "").length() >= 32);
            } catch(Exception ignored){}
            return json.toString();
        }

        @JavascriptInterface public void configure(String endpoint, String token) {
            String base = endpoint.trim().replaceAll("/+$", "");
            if (!base.startsWith("http://") && !base.startsWith("https://")) base = "http://" + base;
            if (!permittedUrl(base)) {
                callback("onConfigured", "{\"error\":\"Use https:// or a private IPv4 LAN address (e.g. http://192.168.1.20:5080).\"}");
                return;
            }
            String actualToken = token.trim().isEmpty() ? prefs.getString("token", "") : token.trim();
            if (actualToken.length() < 32) {
                callback("onConfigured", "{\"error\":\"Pairing token must be at least 32 characters.\"}");
                return;
            }
            prefs.edit().putString("endpoint", base).putString("token",actualToken).apply();
            callback("onConfigured", "{\"success\":true}");
        }

        @JavascriptInterface public void status() {
            executor.execute(() -> {
                try { callback("onStatus", request("GET", "/api/status", null)); }
                catch(Exception e) { callback("onStatus", fail(e)); }
            });
        }

        @JavascriptInterface public void chat(String json) {
            executor.execute(() -> {
                try {
                    JSONObject request = new JSONObject(json);
                    if (!(request.opt("messages") instanceof org.json.JSONArray)) throw new Exception("Invalid message list.");
                    callback("onChat", request("POST", "/api/chat", request.toString()));
                } catch(Exception e) { callback("onChat", fail(e)); }
            });
        }

        private String fail(Exception error) {
            JSONObject json = new JSONObject();
            try { json.put("error", error.getMessage()==null ? "Connection failed" : error.getMessage()); } catch(Exception ignored){}
            return json.toString();
        }
    }

    @Override protected void onDestroy() {
        if (executor != null) executor.shutdownNow();
        if (web != null) {
            web.removeJavascriptInterface("QuillaNative");
            web.destroy();
            web = null;
        }
        super.onDestroy();
    }
}
