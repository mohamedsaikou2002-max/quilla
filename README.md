# Finagler

Finagler is a mobile-friendly TypeScript chat application. The TypeScript server serves the landing and chat pages and securely proxies requests to the user's local LM Studio OpenAI-compatible API. The browser never receives an LM Studio key. The app has no Gemini, IBM Quantum, or quantum simulation integration.

## Run locally

1. Install Node.js 20.6 or newer.
2. Run `npm install`.
3. Copy `.env.example` to `.env` if needed. It is already configured for the LM Studio host and model supplied for this project. Set `LM_STUDIO_API_KEY` only if the local server requires authentication.
4. Start LM Studio's local server and load the configured model.
5. Run `npm run build`.
6. Start with `npm start` and open [http://127.0.0.1:5000](http://127.0.0.1:5000).

For a rebuild followed by startup, run `npm run dev`.

## Mobile support

The landing title scales to the viewport and wraps rather than clipping. Layouts account for device safe areas, narrow screens, landscape phones, and reduced-motion preferences. The chat form uses a mobile-friendly input size and remains scrollable above the on-screen keyboard.

## API

- `GET /api/status` reports whether LM Studio is reachable and whether the configured model is loaded.
- `POST /api/chat` accepts a `messages` list and returns a reply from the configured local model.

Chat requests are limited to 64 KB, 40 message entries, 20 retained turns, and 4,000 characters per message. LM Studio errors are returned without exposing credentials.

## Troubleshooting

- **LM Studio is not reachable:** start its server at the `LM_STUDIO_BASE_URL` in `.env`; confirm `/v1/models` responds from this computer.
- **Model is not loaded:** load the exact `LM_STUDIO_MODEL` in LM Studio, or change `.env` to match an ID returned by `/v1/models`.
- **LM Studio requires a key:** set `LM_STUDIO_API_KEY` in the server's `.env`, then restart. Do not put it in frontend code.
- **Port 5000 is busy:** set a different `PORT` in `.env` and restart.
- **Landing assets look stale:** run `npm run build`, then hard-refresh the page.
