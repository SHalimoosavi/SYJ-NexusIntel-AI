# SYJ NexusIntel AI

### Enterprise SaaS Foundation for Autonomous Revenue Intelligence

> A production-grade multi-tenant platform combining CRM, executive intelligence, and role-based enterprise infrastructure — built to eventually power autonomous AI agents for revenue teams.

[![Status](https://img.shields.io/badge/status-production--stabilisation-yellow)]()
[![Backend](https://img.shields.io/badge/backend-95%25-brightgreen)]()
[![Frontend](https://img.shields.io/badge/frontend-90%25-brightgreen)]()
[![Auth](https://img.shields.io/badge/auth-100%25-brightgreen)]()
[![Deployment](https://img.shields.io/badge/deployment-live-brightgreen)]()

---

## Table of Contents

- [Project Overview](#project-overview)
- [Why NexusIntel AI](#why-nexusintel-ai)
- [Current Status](#current-status)
- [Architecture](#architecture)
- [Features](#features)
- [Backend Modules](#backend-modules)
- [Tech Stack](#tech-stack)
- [Authentication & Security](#authentication--security)
- [Deployment](#deployment)
- [Roadmap](#roadmap)
- [Development Setup](#development-setup)
- [Documentation](#documentation)
- [License](#license)

---

## Project Overview

SYJ NexusIntel AI began as a CRM and business-intelligence prototype. It has since grown into a **multi-tenant SaaS foundation** — with organization management, subscriptions, role-based access control, feature flags, and audit logging sitting underneath a CRM and executive intelligence layer.

The long-term vision is an autonomous multi-agent revenue intelligence system. The current phase is deliberately narrower: **making the enterprise foundation reliable enough to launch on.**

## Why NexusIntel AI

Most CRM and BI tools force a choice: simple tools that don't scale, or enterprise platforms that take months to stand up. NexusIntel AI is built API-first and multi-tenant from day one, so the same foundation that runs a single team today can support organizations, subscriptions, and permissioned access without a re-architecture later.

---

## Current Status

**Phase:** Production Stabilisation
**Goal:** Public Launch
**Focus:** Reliability, authentication, dashboard, CRM, deployment, and bug fixes — not new feature expansion.

| Layer | Completion |
|---|---|
| Backend | 95% |
| Frontend | 90% |
| Authentication | 100% |
| Deployment | 100% |
| Infrastructure | 100% |

This README intentionally leads with what's real and running, not what's planned. Feature-expansion items (AI agents, OSINT, automation) are tracked separately in the [Roadmap](#roadmap) as future phases, not current capabilities.

---

## Architecture

```
Browser
   │
   ▼
Next.js 16 (React 19, TypeScript)
   │
   ▼
JWT Cookie Session
   │
   ▼
Railway-hosted FastAPI
   │
   ▼
RBAC Middleware
   │
   ▼
Business Services
 (Organizations · Subscriptions · Feature Flags · Audit · CRM · Intelligence)
   │
   ▼
SQLAlchemy ORM
   │
   ▼
Railway PostgreSQL
```

Frontend is deployed on Vercel; backend and database are deployed on Railway. Both are live and monitored.

---

## Features

### Enterprise SaaS Foundation
- Organization management with multi-tenant isolation
- Subscription management
- Feature flags per organization/plan
- Role-Based Access Control (RBAC)
- JWT authentication with cookie-based sessions
- Audit logging across sensitive actions

### CRM & Revenue Intelligence
- CRM dashboard for prospect and deal management
- Pipeline visualization
- Revenue analytics and forecasting
- Opportunity tracking through the deal lifecycle
- Executive intelligence briefings

### Platform
- REST API with protected routes and middleware
- Production authentication flow (JWT, RBAC, org isolation)
- Executive dashboard UI

> Autonomous AI agents (Research, Opportunity, Sales, Executive, Memory) are **not yet live**. They are a future roadmap phase — see below.

---

## Backend Modules

```
Authentication
Users
Organizations
Subscriptions
Roles
Feature Flags
Audit Logs
CRM
Executive Intelligence
Agent Memory
Intelligence
Leads
Dashboard
Settings
```

---

## Tech Stack

**Frontend**
- Next.js 16
- React 19
- TypeScript
- TailwindCSS
- Deployed on Vercel

**Backend**
- FastAPI
- SQLAlchemy (Alembic-ready migration architecture)
- JWT authentication
- Deployed on Railway

**Data**
- Railway-managed PostgreSQL

**Services**
- Organization Service
- Subscription Service
- Feature Flag Service
- Audit Service
- Executive Intelligence Service

---

## Authentication & Security

- JWT-based authentication with cookie sessions
- Protected routes enforced via middleware
- Role-Based Access Control across organization boundaries
- Organization-level data isolation
- Audit logging for sensitive/administrative actions

Security posture is being hardened as part of the current stabilisation phase; formal compliance claims (SOC 2, GDPR certification, etc.) will be added here once actually verified rather than stated ahead of time.

---

## Deployment

| Component | Host | Status |
|---|---|---|
| Frontend | Vercel | Live |
| Backend | Railway | Live |
| Database | Railway PostgreSQL | Live |
| Authentication | Production JWT | Live |
| API | Production REST API | Live |
| Dashboard | Production | Live |

---

## Roadmap

### Phase 1 — Production Stabilisation ✅
- Authentication
- RBAC
- Organizations
- Subscriptions
- Feature Flags
- Audit Logs
- Dashboard
- CRM

### Phase 2 — Production Hardening (in progress)
- API validation
- Integration testing
- Frontend stabilization
- Regression testing
- Database validation

### Phase 3 — Public Launch
- Documentation
- Licensing
- Deployment verification
- Commercial readiness

### Future — Feature Expansion
- Autonomous AI agents (Research, Opportunity, Sales, Executive, Memory)
- OSINT engine
- Website audit capabilities
- Outreach automation
- Multi-tenant collaboration tooling

---

## Development Setup

> Setup instructions will be filled in as Phase 2 hardening completes. In the meantime:

```bash
# Clone the repo
git clone https://github.com/SHalimoosavi/<repo-name>.git
cd <repo-name>

# Backend
cd backend
pip install -r requirements.txt
# configure .env with DATABASE_URL, JWT secrets, etc.
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Environment variables and full local setup instructions will be documented in `DEPLOYMENT.md` as part of Phase 3.

---

## Documentation

- Installation Guide — `INSTALL.md`
- Deployment Guide — `DEPLOYMENT.md`
- API Reference — `API.md`
- Features Deep Dive — `FEATURES.md`
- Product Roadmap — `ROADMAP.md`

---

## Built By

**Syed Ali Hasan Moosavi**
Founder & Managing Director, SAYANJALI NEXUS PRIVATE LIMITED

- Portfolio: https://shalimoosavi.github.io/moosavi/
- GitHub: https://github.com/SHalimoosavi
- Email: shalimoosavi@gmail.com

---

## License

```
© 2026 SYJ NexusIntel AI
Developed and maintained by Syed Ali Hasan Moosavi
Under SAYANJALI NEXUS PRIVATE LIMITED
All Rights Reserved.
```

Redistribution and modification are prohibited without written permission. For licensing inquiries, contact shalimoosavi@gmail.com.

---

**Status:** Production Stabilisation · **Goal:** Public Launch
**Last Updated:** July 2026
