import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { createReadStream, existsSync } from "node:fs";
import { extname, join, normalize, resolve, sep } from "node:path";
import { timingSafeEqual } from "node:crypto";

const projectRoot = resolve(process.cwd());
const host = process.env.HOST || "127.0.0.1";
const port = Number(process.env.PORT || 5000);
const lmStudioBaseUrl = (process.env.LM_STUDIO_BASE_URL || "http://127.0.0.1:1234/v1").replace(/\/+$/, "");
const lmStudioModel = process.env.LM_STUDIO_MODEL || "qwen3-vl-8b-glm-4.7-flash-heretic-uncensored-thinking";
const lmStudioApiKey = process.env.LM_STUDIO_API_KEY || "";
const pairToken = process.env.QUILLA_MOBILE_TOKEN || "";
const paired = process.env.QUILLA_PAIRED_MOBILE === "1" && pairToken.length >= 24;
function authorized(request: IncomingMessage): boolean {
 const addr = (request.socket.remoteAddress || "").replace(/^::ffff:/, "");
 if (addr === "127.0.0.1" || addr === "::1") return true;
 if (!paired) return false;
 const o = addr.split(".").map(Number);
 if (o.length !== 4 || o.some(n => !Number.isInteger(n) || n < 0 || n > 255)) return false;
 const [a,b] = o;
 if (!(a === 10 || (a === 172 && b >= 16 && b <= 31) || (a === 192 && b === 168) || (a === 100 && b >= 64 && b <= 127))) return false;
 const supplied = request.headers["x-quilla-device-token"];
 return typeof supplied === "string" && supplied.length === pairToken.length && timingSafeEqual(Buffer.from(supplied),Buffer.from(pairToken));
}


function sendJson(response: ServerResponse, status: number, value: unknown): void {
  response.writeHead(status, { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" });
  response.end(JSON.stringify(value));
}

async function readJson(request: IncomingMessage): Promise<unknown> {
  const chunks: Buffer[] = [];
  let size = 0;
  for await (const chunk of request) {
    const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
    size += buffer.length;
    if (size > 64 * 1024) throw new RangeError("Request body exceeds 64 KB.");
    chunks.push(buffer);
  }
  try { return JSON.parse(Buffer.concat(chunks).toString("utf8")); }
  catch { throw new SyntaxError("Request body must be valid JSON."); }
}

type ChatMessage = { role: "user" | "assistant"; content: string };

async function chat(request: IncomingMessage, response: ServerResponse): Promise<void> {
 if (!authorized(request)) { sendJson(response, 401, {error: "Mobile pairing token missing or incorrect."}); return; }

  let data: unknown;
  try { data = await readJson(request); }
  catch (error) {
    sendJson(response, error instanceof RangeError ? 413 : 400, { error: error instanceof Error ? error.message : "Invalid request." });
    return;
  }
  const rawMessages = (data as { messages?: unknown } | null)?.messages;
  if (!Array.isArray(rawMessages) || rawMessages.length === 0 || rawMessages.length > 40) {
    sendJson(response, 400, { error: "messages must be a non-empty list of at most 40 entries." });
    return;
  }
  const messages: ChatMessage[] = rawMessages.slice(-20).flatMap((item): ChatMessage[] => {
    if (!item || typeof item !== "object") return [];
    const role = (item as { role?: unknown }).role;
    const content = (item as { content?: unknown }).content;
    return (role === "user" || role === "assistant") && typeof content === "string"
      ? [{ role, content: content.slice(0, 4000) }] : [];
  });
  if (!messages.some((item) => item.role === "user" && item.content.trim())) {
    sendJson(response, 400, { error: "Add a non-empty user message." });
    return;
  }
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (lmStudioApiKey) headers.Authorization = `Bearer ${lmStudioApiKey}`;
  try {
    const result = await fetch(`${lmStudioBaseUrl}/chat/completions`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        model: lmStudioModel,
        messages: [{ role: "system", content: "You are Finagler, a helpful assistant. Answer the user's question clearly and directly. Be honest about uncertainty and do not claim to have used external research or tools." }, ...messages],
        temperature: 0.2,
        max_tokens: 1536,
        stream: false,
      }),
      signal: AbortSignal.timeout(120_000),
    });
    if (!result.ok) {
      const errorMessage = result.status === 401 || result.status === 403
        ? "LM Studio requires an API key. Add a current LM_STUDIO_API_KEY to the local .env file and restart."
        : result.status === 404
          ? "LM Studio could not find the configured model. Load it in LM Studio and check LM_STUDIO_MODEL in .env."
          : `LM Studio returned HTTP ${result.status}. Check that the model is loaded and try again.`;
      sendJson(response, result.status === 429 ? 429 : 502, { error: errorMessage });
      return;
    }
    const body = await result.json() as { choices?: Array<{ message?: { content?: string | Array<{ text?: string }> } }> };
    const content = body.choices?.[0]?.message?.content;
    const reply = typeof content === "string" ? content.trim()
      : Array.isArray(content) ? content.map((part) => part.text || "").join("").trim() : "";
    if (!reply) {
      sendJson(response, 502, { error: "LM Studio returned an empty reply. Try again." });
      return;
    }
    sendJson(response, 200, { reply, provider: "lm-studio", model: lmStudioModel });
  } catch (error) {
    const timeout = error instanceof Error && error.name === "TimeoutError";
    sendJson(response, 502, { error: timeout
      ? "LM Studio took too long to answer. Try again or reduce the prompt length."
      : `Cannot connect to LM Studio at ${lmStudioBaseUrl}. Check its server URL and availability.` });
  }
}

async function lmStudioStatus(): Promise<{ connected: boolean; modelLoaded: boolean }> {
  const headers: Record<string, string> = {};
  if (lmStudioApiKey) headers.Authorization = `Bearer ${lmStudioApiKey}`;
  try {
    const response = await fetch(`${lmStudioBaseUrl}/models`, { headers, signal: AbortSignal.timeout(4000) });
    if (!response.ok) return { connected: false, modelLoaded: false };
    const body = await response.json() as { data?: Array<{ id?: string }> };
    const models = body.data || [];
    return { connected: true, modelLoaded: models.some((model) => model.id === lmStudioModel) };
  } catch {
    return { connected: false, modelLoaded: false };
  }
}

function serveFile(pathname: string, response: ServerResponse): void {
  const aliases: Record<string, string> = { "/": "index.html", "/chat": "chatbotpage.html" };
  const publicAssets = new Set(["index.html", "chatbotpage.html", "style.css", "styles.css", "static/js/chat.js", "static/js/landing.js"]);
  const relative = aliases[pathname] || normalize(decodeURIComponent(pathname)).replaceAll("\\", "/").replace(/^[/\\]+/, "");
  if (!publicAssets.has(relative)) {
    sendJson(response, 404, { error: "Not found." });
    return;
  }
  const filePath = resolve(join(projectRoot, relative));
  if (!filePath.startsWith(projectRoot + sep) && filePath !== projectRoot || !existsSync(filePath)) {
    sendJson(response, 404, { error: "Not found." });
    return;
  }
  const mime: Record<string, string> = { ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8" };
  response.writeHead(200, { "Content-Type": mime[extname(filePath)] || "application/octet-stream", "X-Content-Type-Options": "nosniff" });
  createReadStream(filePath).pipe(response);
}

const server = createServer((request, response) => {
  const url = new URL(request.url || "/", `http://${request.headers.host || "localhost"}`);
  if (request.method === "GET" && url.pathname === "/api/status") {
    void lmStudioStatus().then((lmStudio) => sendJson(response, 200, {
      status: "online", aiEnabled: true, provider: "lm-studio", model: lmStudioModel, ...lmStudio,
    }));
  } else if (request.method === "POST" && url.pathname === "/api/chat") {
    void chat(request, response);
  } else if (request.method === "GET") {
    serveFile(url.pathname, response);
  } else {
    sendJson(response, 404, { error: "Not found." });
  }
});

server.listen(port, host, () => {
  console.log(`Finagler running at http://${host}:${port} (LM Studio: ${lmStudioBaseUrl}; model: ${lmStudioModel})`);
});
