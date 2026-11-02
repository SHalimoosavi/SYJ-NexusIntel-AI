# Legacy Hosting Notes — Deprecated

> **DEPRECATED — DO NOT USE FOR NEW DEPLOYMENTS.**
>
> SYJ NexusIntel AI is moving to a self-hosted Docker Compose deployment. These notes are retained only to explain historical repository configuration. They are not supported installation instructions.

## Former hosting layout

The previous deployment split the Next.js frontend across Vercel and the FastAPI backend plus PostgreSQL across Railway. The repository formerly contained a Railway `Procfile` and `backend/railway.json`. Those deployment files are being retired.

## Current direction

- Use the Docker-based self-hosted deployment documented by the forthcoming `INSTALL.md` and `DEPLOYMENT.md`.
- Do not create new Vercel or Railway deployments for this repository.
- The repository owner is responsible for disconnecting the Vercel Git integration and related GitHub settings in the provider dashboards.
- No credentials from the former hosting environment are trusted. Any credential ever committed to Git history must be rotated or retired.
- Native Windows/Linux installers, iOS packaging and commercial licensing are not supported by this migration.

## Historical note

The former cloud-hosting arrangement is recorded here for audit traceability only. No provider credentials, deployment tokens, environment values or secrets are stored in this document.
