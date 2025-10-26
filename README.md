# Functional Traces with OpenTelemetry, Grafana Tempo & Docker Compose

This repository provides a ready‑to‑run stack to **collect functional application traces** via a small HTTP gateway
(FastAPI + OpenTelemetry SDK), forward them to an **OpenTelemetry Collector**, and visualize them in **Grafana**
(with **Tempo** as the trace backend).

## What you get

- **gateway**: HTTP `/ingest` endpoint (FastAPI) to accept functional events.
  - Enforces an **API key** (`X-API-Key`) to identify the client.
  - Computes a **hashed user id** from email using **HMAC‑SHA256** with a secret salt.
  - Emits an OpenTelemetry **span** named `functional_event` with your attributes.
- **otel-collector**: Receives spans over OTLP and forwards them to Tempo.
- **tempo**: Stores traces locally (no external dependencies).
- **grafana**: Pre-provisioned with a Tempo datasource so you can explore traces immediately.

> **Why a gateway?**  
> Sending OTLP directly from curl/Thunderbird 60 is impractical (binary protobuf). The gateway gives you a simple, secure HTTP
> JSON interface and still emits standard OTLP to the collector/Tempo.

## Quick start

1. Copy `.cd ..
1. env.sample` to `.env` and **edit** the secrets:
   ```bash
   cp .env.sample .env
   # Edit HASH_SALT and API_KEYS
   ```

2. Launch the stack:
   ```bash
   docker compose up -d --build
   ```

3. Send a test event (replace `YOUR_API_KEY` with a value from `.env`):
   ```bash
   curl -X POST http://localhost:8080/ingest      -H "Content-Type: application/json"      -H "X-API-Key: YOUR_API_KEY"      -d '{
       "user_email": "alice@example.org",
       "app_id": "thunderbird-plugin-iaassistant",
       "message": "export carnet contacts terminé",
       "attributes": {"count": 42, "result": "ok"}
     }'
   ```

4. Open Grafana:
   - URL: <http://localhost:3000>
   - User/Pass: `admin` / `admin`
   - Go to **Explore → Tempo**, search by **Span name** = `functional_event`, or filter by attributes like `app.id`.

## Architecture

```
client (curl / Python / Thunderbird JS)
        ⇣  HTTP JSON + X-API-Key
gateway (FastAPI) ──OTLP gRPC──> OpenTelemetry Collector ──> Tempo
                                                         ⇡
                                                     Grafana (Explore)
```

## Message schema

`POST /ingest` body:
```json
{
  "user_email": "alice@example.org",
  "app_id": "my-application",
  "message": "functional message to log as a trace",
  "attributes": { "key": "value" }   // optional additional attributes
}
```

Required header:
- `X-API-Key: <one of the keys listed in your .env API_KEYS>`

What gets stored in the span attributes:
- `user.hash`         : HMAC-SHA256(email_normalized, HASH_SALT)
- `app.id`            : your `app_id`
- `event.message`     : your `message`
- `client.api_key_id` : last 6 chars of the provided API key (for identification without storing the full secret)
- `client.ip`, `http.user_agent` (best effort from request)
- Any `attributes` you supply are merged under their own keys.

## Examples

See the [`examples/`](examples/) folder for ready-to-run snippets:

- `curl.sh` – minimal curl example
- `python/send_event.py` – simple Python script using `requests`
- `thunderbird60/js_example.js` – example snippet suitable for a Thunderbird 60.9.1 add‑on background or module.
  Uses `XMLHttpRequest` to keep compatibility with ESR 60.

## Security notes

- The API key is a **shared secret**; rotate it frequently. You can list multiple keys in `.env` (`API_KEYS` comma-separated).
- The **hashed user id** uses HMAC‑SHA256 with a secret `HASH_SALT`. Do **not** commit real salts to VCS.
- Only hashed user identifiers are persisted in traces, **never raw emails**.

## Clean up

```bash
docker compose down -v
```

---

Made for quick developer trials; adapt for production (TLS, reverse proxy, secret management, multi‑tenant auth, persistence).
