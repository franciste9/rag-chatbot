# Dev Spec: Per-IP Rate Limiting (Flask-Limiter)

## Objective

Protect the billed endpoints (`/api/documents/upload` → OpenAI embeddings, `/api/chat` and `/api/search` → OpenAI + Claude) from cost abuse by anonymous clients once the app is publicly deployed. Anonymous per-IP rate limiting; no authentication, no CAPTCHA — the demo must stay click-and-try.

## Context (read first)

- Flask app in `backend/main.py`; routes: `/api/documents/upload`, `/api/search`, `/api/chat`, `/api/health`, plus static frontend routes.
- Deployed on Railway via `Procfile`: gunicorn, **2 workers**. Railway terminates TLS and proxies requests, so the client IP arrives in `X-Forwarded-For`.
- `backend/config.py` centralizes env var reads. Dependencies are pinned exactly in `requirements.txt` — keep it that way.
- Workflow: feature branch off `main`, conventional commits (one logical change per commit), PR to `main`. Do not commit directly to `main`.

## Requirements

### 1. Dependency
- Add `Flask-Limiter` to `requirements.txt`, pinned to the latest stable exact version. Install into the existing `venv`.

### 2. Trust the proxy (prerequisite for correct IPs)
- Wrap the WSGI app with `werkzeug.middleware.proxy_fix.ProxyFix` with `x_for=1, x_proto=1, x_host=1` so `request.remote_addr` reflects the real client IP behind Railway's single proxy hop — otherwise every visitor shares the proxy's IP and one abuser rate-limits everyone.

### 3. Limiter setup
- Initialize `Limiter` with `key_func=get_remote_address`, explicit `storage_uri="memory://"`, and `default_limits=["200 per hour"]`.
- Per-route limits (decorators):
  - `/api/documents/upload`: `5 per hour` (most expensive: embedding a whole PDF)
  - `/api/chat`: `20 per hour`
  - `/api/search`: `30 per hour`
- Exempt `/api/health` and the static/frontend routes from all limits.
- Define the limit strings as constants in `backend/config.py`, overridable via env vars (`RATE_LIMIT_UPLOAD`, `RATE_LIMIT_CHAT`, `RATE_LIMIT_SEARCH`) with the above defaults.

### 4. Error handling
- Add a 429 error handler returning JSON consistent with the existing API error shape: `{"error": "Rate limit exceeded. Try again later."}` with status 429. Include the `Retry-After` header (Flask-Limiter sets this if `headers_enabled=True` — enable it).
- Frontend (`frontend/script.js`): when a response has status 429, show a friendly message ("You've hit the demo's rate limit — try again in a bit") instead of the raw error.

### 5. Documentation
- `README.md` → Production Considerations: document the limits, and note the known limitation that `memory://` storage is **per gunicorn worker** (2 workers ⇒ effective limits up to 2×; acceptable for a demo, Redis storage is the production fix).
- `CLAUDE.md`: add a short paragraph describing the rate limiting setup (limits, ProxyFix, per-worker caveat).

## Acceptance criteria

1. `python -m py_compile backend/*.py` passes; app starts locally with no Flask-Limiter warnings.
2. `for i in $(seq 1 7); do curl -s -o /dev/null -w "%{http_code}\n" -X POST -F "file=@samplepdf/sample1page.pdf" http://localhost:5001/api/documents/upload; done` → first 5 return 200, then 429 with JSON body and `Retry-After` header. (Run with dummy/real keys as appropriate; a 500 from missing keys still proves the limiter fires first only if it returns 429 — prefer testing with real keys locally.)
3. `/api/health` never returns 429 regardless of request volume.
4. Frontend shows the friendly message on 429.
5. README and CLAUDE.md updated; `requirements.txt` still fully pinned.

## Out of scope

Redis-backed storage, authentication/API keys, CAPTCHA, request queuing, per-user quotas. Do not refactor unrelated code.

## Commit plan (suggested)

1. `build: add Flask-Limiter (pinned)`
2. `feat(api): per-IP rate limits on billed endpoints with ProxyFix`
3. `feat(frontend): friendly message on 429`
4. `docs: document rate limits and per-worker caveat`
