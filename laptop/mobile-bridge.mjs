/**
 * QUILLA mobile bridge. Keeps the original QUILLA and LM Studio bound to localhost;
 * exposes ONLY the minimal token-protected chat and status API to a trusted LAN.
 * No dependency packages required. Requires Node.js 20.6+.
 */
import { createServer } from 'node:http';
import { randomBytes, timingSafeEqual } from 'node:crypto';

const host = process.env.QUILLA_BRIDGE_HOST || '0.0.0.0';
const port = Number(process.env.QUILLA_BRIDGE_PORT || '5080');
const base = (process.env.QUILLA_UPSTREAM_URL || 'http://127.0.0.1:5000').replace(/\/+$/, '');
const secret = process.env.QUILLA_MOBILE_TOKEN || '';
if (secret.length < 32 || secret.length > 256 || /\s/.test(secret)) {
  throw new Error('Set QUILLA_MOBILE_TOKEN to a unique 32+ character random token in laptop/.env');
}
if (!/^http:\/\/127\.0\.0\.1:\d+$/.test(base) && !/^http:\/\/\[::1\]:\d+$/.test(base)) {
  throw new Error('QUILLA_UPSTREAM_URL must target a local loopback server (e.g. http://127.0.0.1:5000).');
}
if (!Number.isSafeInteger(port) || port < 1024 || port > 65535) throw new Error('Invalid bridge port');
const expected = Buffer.from(secret, 'utf8');
const json = (res, status, data) => {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' });
  res.end(JSON.stringify(data));
};
const authorized = (value) => {
  if (typeof value !== 'string' || !value.startsWith('Bearer ')) return false;
  const bytes = Buffer.from(value.slice(7), 'utf8');
  return bytes.length === expected.length && timingSafeEqual(bytes, expected);
};
const readBody = async(req) => {
  let size = 0; const parts = [];
  for await (const part of req) {
    size += part.length;
    if (size > 64*1024) {const err = new Error('Request exceeds 64KB.');err.httpStatus=413;throw err;}
    parts.push(part);
  }
  const payload = Buffer.concat(parts).toString('utf8');
  const parsed = JSON.parse(payload);
  if (!parsed || !Array.isArray(parsed.messages) || parsed.messages.length<1 || parsed.messages.length>40) {
    const err = new Error('Provide 1–40 chat messages.');err.httpStatus=400;throw err;
  }
  for (const m of parsed.messages) {
    if (!m || !['user','assistant'].includes(m.role) || typeof m.content !== 'string' || m.content.length>4000) {
      const err=new Error('Invalid chat message.');err.httpStatus=400;throw err;
    }
  }
  return JSON.stringify({ messages: parsed.messages });
};

const server = createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', 'null'); // Native app sends no CORS requests; browsers cannot use cross-origin JS.
  res.removeHeader('Access-Control-Allow-Origin');
  if (!authorized(req.headers.authorization)) {json(res, 401, {error:'Pairing token missing or incorrect.'});return;}
  const route = (req.url || '').split('?')[0];
  if (!((req.method === 'GET' && route === '/api/status') || (req.method === 'POST' && route === '/api/chat'))) {
    json(res, 404, {error:'Not found.'});return;
  }
  try {
    const payload = req.method === 'POST' ? await readBody(req) : undefined;
    const upstream = await fetch(base+route, {
      method:req.method,
      headers:payload?{'Content-Type':'application/json'}:{},
      body:payload,
      redirect:'error',
      signal:AbortSignal.timeout(route==='/api/chat'?122000:5500)
    });
    if(!upstream.ok) {json(res,502,{error:'Local QUILLA returned HTTP '+upstream.status});return;}
    const ct=upstream.headers.get('content-type')||'';
    if(!ct.includes('application/json')) throw Error('Invalid upstream response type');
    const output=await upstream.text();
    if(Buffer.byteLength(output)>256*1024) throw Error('Upstream response too large');
    json(res,200,JSON.parse(output));
  } catch(err) {
    const status=err.httpStatus||((err instanceof SyntaxError)?400:502);
    json(res,status,{error:status===502?'Laptop QUILLA backend unavailable or timed out.':err.message});
  }
});
server.requestTimeout=130000;
server.headersTimeout=10000;
server.listen(port,host,()=>console.log(`QUILLA mobile bridge listening on ${host}:${port} (secured API only).`));
