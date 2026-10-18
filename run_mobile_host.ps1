$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path node_modules)) { npm ci; if ($LASTEXITCODE -ne 0) { throw 'npm install failed' } }
npm run build
if ($LASTEXITCODE -ne 0) { throw 'TypeScript build failed' }
try { $models = @( (Invoke-RestMethod 'http://127.0.0.1:1234/v1/models' -TimeoutSec 5).data ) }
catch { throw 'Start LM Studio at 127.0.0.1:1234 and load an abliterated GGUF model first.' }
if ($models.Count -eq 0 -or -not $models[0].id) { throw 'No LM Studio model loaded' }
$tokenFile = Join-Path $PSScriptRoot '.quilla_mobile_pairing_token'
if (-not (Test-Path $tokenFile)) { $token = py -c 'import secrets; print(secrets.token_urlsafe(32))'; Set-Content $tokenFile $token -NoNewline }
else { $token = (Get-Content $tokenFile -Raw).Trim() }
$env:HOST = '0.0.0.0'
$env:PORT = '5000'
$env:QUILLA_PAIRED_MOBILE = '1'
$env:QUILLA_MOBILE_TOKEN = $token
$env:LM_STUDIO_BASE_URL = 'http://127.0.0.1:1234/v1'
$env:LM_STUDIO_MODEL = $models[0].id
Write-Host "QUILLA model: $env:LM_STUDIO_MODEL"
Write-Host "Pairing token: $token" -ForegroundColor Yellow
Write-Host 'Use ipconfig to get Wi-Fi IPv4, then enter IP:5000 and the token in the Android app.'
Write-Host 'Use trusted private Wi-Fi ONLY. Never forward port 5000 to the public internet.'
node .server-build/index.js
