# Network Hardening and Deployment Topology

## Reverse-proxy recommendation: Nginx

Nginx is selected for the self-hosted topology because request-rate zones, connection limits, request-body caps, timeouts and compression are built into the standard distribution. Caddy has simpler automatic certificate management, but its rate-limiting directive requires a third-party module. Nginx therefore gives this project a smaller and more auditable proxy feature set; Certbot is used for ACME certificate issuance and renewal.

## Self-hosted Docker topology

```text
Internet
   |
Nginx :80/:443 (172.30.0.2)
   |--------------------|
Frontend :3000       Backend :8000 (172.30.0.3)
                         |
                      Redis (private data network)
```

- Only Nginx publishes host ports 80 and 443.
- Frontend and backend ports are exposed only inside the Docker bridge network; the backend has no host-published port.
- Redis is on an internal-only network and has no published port.
- The backend trusts forwarded headers only from the fixed Nginx address `172.30.0.2`. Nginx overwrites `X-Real-IP` and `X-Forwarded-For` with the socket peer address rather than appending caller-supplied values.
- Backend process runs with `--no-proxy-headers`; the application-level Uvicorn ProxyHeadersMiddleware is the only forwarding-header parser and has an explicit trusted-host list.
- Redis is mandatory in production. The application returns 503 if it is unavailable rather than silently switching to process-local counters.
- Set `COOKIE_SAMESITE=lax` because browser and API share the same site. Set `COOKIE_SECURE=true`.

### First-time TLS setup

1. Copy root `.env.example` to `.env`; set a real domain, ACME email, database URL and freshly generated JWT keyring. Do not commit `.env`.
2. Point the domain's A/AAAA records at the host and open inbound TCP 80/443.
3. Start the HTTP-only ACME bootstrap listener and app services:
   `docker compose --profile bootstrap up -d nginx-bootstrap backend frontend redis`
4. Issue the first certificate:
   `docker compose --profile renewal run --rm --entrypoint certbot certbot-renew certonly --webroot -w /var/www/certbot -d "$DOMAIN" --email "$ACME_EMAIL" --agree-tos --no-eff-email`
5. Stop the bootstrap listener and start the TLS listener:
   `docker compose --profile bootstrap stop nginx-bootstrap`
   `docker compose --profile tls up -d nginx`
6. Start the renewal loop:
   `docker compose --profile renewal up -d certbot-renew`

Certbot checks for renewal every 12 hours. The Nginx container reloads its configuration/certificates every six hours. Monitor the Certbot container logs and certificate expiry; this is automated renewal, not a substitute for alerting. The first issuance is necessarily a one-time bootstrap operation.

### Proxy controls

The supplied Nginx configuration includes:
- Per-IP API request rate zone and a stricter authentication zone.
- Per-IP concurrent connection limits.
- 10 MB request-body cap at Nginx and a streaming 10 MB ASGI cap in FastAPI, including chunked requests.
- Header/body/send timeouts to constrain slow clients.
- Upstream connect/read/send timeouts.
- gzip compression for text, JSON, CSS, JS and SVG.
- TLS 1.2/1.3, HSTS, frame/content/referrer/permissions headers, version-banner suppression and upstream server-header hiding.

The Next.js Proxy creates a fresh per-request CSP nonce for page rendering. Script execution is nonce-bound and does not use `unsafe-inline`; `style-src-attr 'unsafe-inline'` remains a narrow compatibility exception for the existing Framer Motion inline style attributes. Review browser CSP reports before tightening this further. Nonce-based CSP requires dynamic rendering and may reduce static optimization/ISR opportunities.

## Vercel frontend + Railway backend

This split-hosted setup is not equivalent to the private Docker topology:

- Set Vercel `NEXT_PUBLIC_API_BASE_URL` to the Railway HTTPS API origin. Never put JWT signing keys or backend secrets in `NEXT_PUBLIC_*` variables.
- Set Railway `APP_ENV=production`, `REDIS_URL`, `JWT_SIGNING_KEYS`, `JWT_ACTIVE_KID`, `CORS_ORIGINS` to the exact Vercel/custom frontend origins, and `TRUSTED_PROXY_HOSTS=127.0.0.1,::1`.
- Railway start command deliberately uses `--no-proxy-headers`; do not use `--forwarded-allow-ips=*`. The app-level proxy middleware trusts only loopback. This prevents spoofed forwarded headers from being treated as a client IP.
- Railway's public edge rewrites forwarding headers, but its container-facing proxy peer addresses are not a stable published allowlist. Private-network callers bypass the public edge and can supply their own forwarding headers. Therefore the app must not trust `X-Forwarded-For` or `X-Real-IP` on this split deployment without a separately verified network trust boundary. Rate limiting by IP may consequently see a shared edge peer rather than individual client IPs; authenticated user/organization quotas remain active.
- Vercel's `proxy.ts` and `next.config.ts` apply frontend CSP/security headers. FastAPI applies API response headers. CORS and cookie Origin checks use the explicit `CORS_ORIGINS` allowlist.
- Use `COOKIE_SECURE=true` and `COOKIE_SAMESITE=none` only if frontend/API are genuinely cross-site. Prefer custom subdomains under the same registrable domain (for example, `app.example.com` and `api.example.com`) to reduce third-party-cookie restrictions. Confirm browser behavior before release.
- **Residual reachability limitation:** a Vercel frontend cannot reach a Railway private-only service through Railway's private network. With the current split, the Railway API needs a public ingress and is still network-reachable directly. CORS is not an access-control boundary. A private-only backend requires moving the BFF/frontend into the same private network or adding a separately approved authenticated ingress/edge design. This branch does not claim the split Vercel/Railway backend is unreachable directly.

## Local and desktop mode

- Set `APP_ENV=desktop` (or `development`) to enable the process-local rate-limit fallback.
- Bind FastAPI to `127.0.0.1`, not `0.0.0.0`, for a native local desktop process.
- Use `--no-proxy-headers` and leave `TRUSTED_PROXY_HOSTS` empty when there is no local reverse proxy. If a local Nginx proxy is used, trust only its loopback address.
- Use `COOKIE_SECURE=false` only for plain-HTTP loopback development. Production always requires secure cookies.
- Do not use in-memory rate limiting in multi-process or hosted production deployments.

## Railway and proxy-header trust evidence

Railway documents `X-Real-IP`, `X-Forwarded-Proto` and `X-Forwarded-Host` as edge headers, but a Railway support clarification notes that container-facing proxy addresses are not stable and private-network callers bypass the edge header rewriting. This is why the supplied Railway start command ignores forwarded headers instead of trusting a wildcard or guessed CIDR.

References:
- Railway public networking headers and limits: https://docs.railway.com/networking/public-networking/specs-and-limits
- Railway proxy trust clarification: https://station.railway.com/questions/security-clarification-x-forwarded-for-fb0bba28
- FastAPI trusted proxy guidance: https://fastapi.tiangolo.com/advanced/behind-a-proxy/
- Next.js 16 Proxy convention: https://nextjs.org/docs/app/api-reference/file-conventions/proxy
- Next.js CSP nonce guidance: https://nextjs.org/docs/13/pages/building-your-application/configuring/content-security-policy

## Not yet verified

- Docker image builds and Compose config validation were not run in this session.
- Nginx syntax validation, TLS issuance/renewal, browser CSP compatibility and proxy-header spoof tests remain pending.
- The split Vercel/Railway backend remains publicly reachable at the network layer. Do not describe it as private or direct-access blocked.
