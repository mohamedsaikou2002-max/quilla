# QUILLA for Android — laptop-hosted chatbot

## What is included
This adds an Android **native WebView UI** to your existing GitHub `mohamedsaikou2002-max/quilla` chat project without replacing or exposing its original TypeScript backend. The package uses the exact user-provided black-and-white neuron image for the app launcher icon and the interface. The Android app connects through a 32+ character token-protected local bridge to QUILLA's existing chat API. QUILLA then uses the local OpenAI-compatible LM Studio API. **The model runs on the laptop, not on the phone.**

This is the chat function of the currently available GitHub QUILLA repository, not a port of its separately described quantum, engineering, corpus, or payment features.

## Laptop setup (Windows / PowerShell)

1. Install Node.js 20.6+ and LM Studio. In LM Studio, install and load an abliterated GGUF model, or keep your currently configured model if installed. For an 8B starter option, see Huihui-Qwen3-8B-abliterated-v2 (Q4_K_M, approximately 5.1 GB on disk): https://huggingface.co/mradermacher/Huihui-Qwen3-8B-abliterated-v2-GGUF . The 5.1 GB is model-file size, not total memory required; CPU-only inference may be slow. Enable the LM Studio **Developer > Start Server** option on **localhost only**, typically port 1234. LM Studio `/v1/models` provides the exact ID of your loaded model.
2. Clone or open your *existing* QUILLA repository:

```powershell
git clone https://github.com/mohamedsaikou2002-max/quilla.git
cd quilla
npm install
Copy-Item "path\to\QUILLA-Android\laptop\quilla-server.env.example" .env
# Edit LM_STUDIO_MODEL in .env to EXACTLY match one of the IDs below:
(Invoke-RestMethod http://127.0.0.1:1234/v1/models).data.id
npm run build
npm start
```

3. In **a second PowerShell window**, extract this ZIP and configure the mobile bridge:

```powershell
cd "path\to\QUILLA-Android"
Copy-Item .\laptop\.env.example .\laptop\.env
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
# Copy the random token and set QUILLA_MOBILE_TOKEN in laptop/.env.
node --env-file=laptop/.env laptop/mobile-bridge.mjs
```

4. Find the Windows laptop's LAN IPv4 address with `ipconfig` and allow inbound TCP 5080 *only on the Private profile and trusted local subnet* in Windows Firewall. Keep TCP 1234 (LM Studio) and TCP 5000 (QUILLA) **local-only**; do not port-forward any of them. Both phone and laptop should be on the same trusted Wi-Fi network.
5. Open QUILLA on Android → settings → `http://YOUR_LAPTOP_IP:5080` → paste pairing token → **Save & test**. The status indicator will turn green when the backend and selected model are reachable.

**Security:** This initial LAN option uses HTTP and a bearer token, so the token and chat content are not encrypted against LAN sniffing. Use only on a network you trust; for untrusted Wi-Fi or remote access put the bridge behind authenticated **HTTPS/Tailscale**. Avoid putting the model, bridge, or development servers on the public Internet. Token is saved in the app's private preferences; no Android backup is allowed.

## Build an installable debug APK

Open the `android` folder in Android Studio (JDK 17; Android SDK 35), synchronize Gradle, then **Build → Build Bundle(s) / APK(s) → Build APK(s)**. The installable output is `android/app/build/outputs/apk/debug/app-debug.apk`.

Or, from a machine with Android SDK 35, Gradle 8.9, and Java 17:

```powershell
cd android
gradle assembleDebug
```

A workflow is provided in `.github/workflows/android-debug-apk.yml` for builds on GitHub Actions once these Android files are checked into your repository. Debug APKs are signed with the development key; **not release-signed** and not ready for Play Store.

## Model notes

The current GitHub backend has `LM_STUDIO_MODEL=qwen3-vl-8b-glm-4.7-flash-heretic-uncensored-thinking` as a default model *identifier*. That does not verify model availability. Replace it with the exact local ID from `/v1/models`. A 7–8B abliterated GGUF quantized at Q4 is a reasonable starting point if your laptop has sufficient RAM (16 GB system memory is preferable, depending on GPU offload and context length). Abliteration reduces model refusals; it does not guarantee factuality, reasoning quality, or security. Do not grant untrusted models direct shell, filesystem, or browser privileges.

## Verification

After starting LM Studio + QUILLA + bridge, run:

```powershell
$token = 'PASTE_YOUR_TOKEN'
Invoke-RestMethod -Uri http://127.0.0.1:5080/api/status -Headers @{Authorization="Bearer $token"}
```

Expect `connected: true` and `modelLoaded: true` when the configured model is loaded. A missing/wrong bearer token must return HTTP 401. Chat output comes from the installed LM Studio model, not a mock.