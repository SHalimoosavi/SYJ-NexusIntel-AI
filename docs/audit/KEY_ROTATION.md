# JWT Signing-Key Rotation Runbook

## Scope and safety

Every JWT signing key ever committed to Git is compromised, even if later removed. Never paste a key into Git, a ticket, chat, logs, or this runbook. Do not retain an exposed key as a verification fallback.

## 1. Generate a replacement key

On a trusted local machine, generate 48 cryptographically random bytes:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the generated value directly into the deployment secret manager. Do not put it in a tracked file or shell command history. Choose a new non-secret key ID, for example `jwt-2026-11-rotation-1`.

## 2. Configure the backend

Set both variables in the environment that runs FastAPI:

- `JWT_ACTIVE_KID`: the new key ID.
- `JWT_SIGNING_KEYS`: a JSON object mapping the new key ID to the generated value, e.g. `{"jwt-2026-11-rotation-1":"<GENERATED_VALUE>" }`. Replace the angle-bracket placeholder locally; never commit this example.

### Railway

Open the Railway project, select the **backend service**, then **Variables**. Set `JWT_ACTIVE_KID` and `JWT_SIGNING_KEYS` there. Apply/redeploy the backend service. Do not put either value in Railway build logs or repository variables.

### Vercel

Only if the FastAPI backend itself is deployed on Vercel, set both variables in that backend project's **Settings → Environment Variables** for each relevant environment, then redeploy. If Vercel hosts only the Next.js frontend, do **not** add the signing key to the frontend. Never use a `NEXT_PUBLIC_*` variable for secrets.

### Local development and Docker

For local FastAPI development, put both variables in the untracked `backend/.env`. For root Docker Compose, put them in the untracked root `.env` used by Compose. Both files are excluded by `.gitignore`; verify with `git check-ignore` before adding files. The checked-in `.env.example` files contain placeholders only.

## 3. Invalidate existing sessions and tokens

1. Remove every old signing key from `JWT_SIGNING_KEYS`; do not keep it as a previous/overlap key.
2. Set `JWT_ACTIVE_KID` to the new ID and deploy all backend instances.
3. Tokens signed with the removed key will fail verification, forcing users to authenticate again. This invalidates outstanding access and refresh JWTs signed with that key.
4. Clear/revoke any server-side refresh-token or session records using the application's supported revocation mechanism. If session-version records are persisted, increment/revoke them for all users through the supported application/DB procedure. Do not issue a global Redis flush on a shared instance.

## 4. Verify safely

- Confirm the backend deployment completed and its non-secret health check is healthy.
- Confirm startup fails when `JWT_SIGNING_KEYS` is absent, contains a value shorter than 32 UTF-8 bytes, or contains a known placeholder/default. The automated unit tests cover these cases.
- Sign in with a test account and confirm newly issued JWT headers contain the configured active `kid`.
- Confirm a previously issued session is rejected after the old key is removed, using a controlled test session. Do not test the exposed historical key against any live service.
- Record only date, environment, service, operator, deployment ID and pass/fail evidence. Never record the key itself.

## 5. Rollback warning

Do not restore a compromised key as a rollback. If deployment fails, generate another fresh key, update both variables, and redeploy. History purge is a separate operation and is not authorized by this runbook.
