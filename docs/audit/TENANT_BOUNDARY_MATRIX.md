# Tenant Boundary and API Exposure Matrix

**Branch:** `feat/security-hardening`  
**Status:** Source review and automated regression tests added; CI execution pending.

## Enforcement model

- All non-public API routes must transitively depend on `get_current_user`, including routes protected through `require_roles` and `require_feature`.
- The tenant ID is read from the current active user row in PostgreSQL, not trusted from JWT tenant claims or request bodies.
- Business queries are scoped by the current `organization_id`; ID-based mutations first fetch the target using both record ID and organization ID.
- Organization-wide administration is restricted to `SUPER_ADMIN`; organization owners/managers are scoped to their own tenant.
- Tenant mismatch returns a not-found response for ID-addressable resources where practical, avoiding cross-tenant existence disclosure.
- Responses use explicit Pydantic models for ORM-backed records. User password hashes, organization foreign keys on user/invitation responses, audit actor/tenant IDs and report filesystem paths are excluded.
- Invitation creation returns its opaque bearer token once to the authorized inviter because the current product has no mail-delivery integration. The token is hashed before database storage and omitted from invitation-list responses. Treat the creation response as secret-bearing.

## Endpoint coverage

| Endpoint family | Methods / operations | Tenant boundary / authorization | Regression coverage |
|---|---|---|---|
| `/auth` | login, refresh, logout, change-password | Public entry points validate Origin; refresh JTI single-use; cookie CSRF check; active DB user/session version; logout/password change revoke session family | `test_auth_dependencies.py`, `test_jwt_rotation.py`, auth route checks |
| `/leads` | create, list, update, delete | Organization ID injected from authenticated DB user; ID updates/deletes scoped by both lead ID and tenant | `test_tenant_isolation.py` service and API IDOR tests |
| `/activities`, `/lead-notes` | create, list by lead, delete note | Parent lead must belong to tenant; activity/note reads and deletes filter tenant | `test_tenant_isolation.py` |
| `/agent-memory` | save, history, latest | Tenant ID server-assigned; domain validation; all reads scoped by tenant | `test_tenant_isolation.py`, response schema tests |
| `/users` | list, read, role/status update, delete | Tenant-scoped user lookup; role assignment allowlist; self/owner/super-admin escalation guards | `test_tenant_isolation.py` and RBAC tests |
| `/organizations` | create, list, read | Create and global list require SUPER_ADMIN; tenant owner/manager/viewer can read only their organization | API IDOR and RBAC tests |
| `/subscriptions` | create, list, read | Create/list require SUPER_ADMIN; tenant roles may read only their own subscription | API IDOR and RBAC tests |
| `/invitations` | create, list, accept | Create/list scoped to current tenant; role assignment constrained; accept requires matching email and one-time token | tenant service/API tests; invitation token storage reviewed |
| `/audit` | logs, event summary | Tenant-scoped read; no tenant-facing update/delete endpoint; ORM guards plus PostgreSQL trigger/grants supplied | tenant service/API tests; database trigger not yet applied |
| `/dashboard`, `/organization-dashboard`, `/crm`, `/executive-intelligence`, `/relationship-intelligence`, `/revenue-forecast`, `/sales-agent` | analytical reads/generation | Current organization ID passed from authenticated user; service queries filter organization | analytics service regression test; CI pending |
| `/osint`, `/technology`, `/intelligence`, `/lead-qualification`, `/opportunity`, `/multi-agent`, `/reports`, `/business-discovery` | external domain analysis / discovery | Authenticated tenant context; per-organization AI usage limits; validated public-domain inputs; explicit response models | auth-route coverage; domain/SSRF and schema tests pending expansion |
| `/health`, `/` | status | Intentionally public, no tenant data | exempted by route-auth inventory test |
| `/invitations/accept` | accept invitation | Intentionally public bearer-token flow; token digest, email binding, expiry and single-use check | invitation service review; endpoint integration test pending |

## Automated checks added

- `test_api_routes_require_authentication_except_explicit_public_routes`: walks FastAPI dependency trees and fails if any API route outside the explicit public allowlist does not depend on `get_current_user`.
- Tenant A/B fixture tests for organization, lead, activity, notes, agent memory, audit logs, invitations, subscriptions and user administration.
- API IDOR tests use guessed Tenant B record IDs while authenticated as Tenant A.
- Analytics service tests exercise CRM, executive dashboard/intelligence, organization dashboard, relationship intelligence, forecast and sales-priority services using Tenant A context.
- RBAC tests reject owner-to-owner role escalation and super-admin-only organization/subscription operations.
- Response schema tests assert sensitive fields are omitted.

## Known limitations

1. These tests have been authored but not yet confirmed passing in GitHub Actions.
2. Application-level tenant filters are not PostgreSQL Row-Level Security. A future RLS migration would provide defense in depth, but requires transaction-scoped tenant context and a separately approved migration.
3. Some analytics and external-analysis routes have response models, but not every route has a dedicated adversarial payload test yet. The route-auth inventory proves authentication dependency presence, not full data correctness for every code path.
4. The super-admin role is currently global in RBAC but some list endpoints remain tenant-scoped by the current user's organization. A separate global admin data-access model has not been implemented.
5. No live production data or credentials were used.
