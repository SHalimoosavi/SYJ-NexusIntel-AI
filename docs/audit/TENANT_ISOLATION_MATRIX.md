# Tenant Isolation and Response-Surface Matrix

Reviewed against `feat/security-hardening`. This is a source-level inventory, not a completed penetration test.

## Tenant-bound route inventory

| Router / route family | Auth / role boundary | Tenant source | Current source-level control | Verification |
|---|---|---|---|---|
| `/leads` list/create/update/delete | `get_current_user` | DB user organization | Lead service filters by `organization_id`; guessed IDs return not-found | Service regression tests added |
| `/activities` create/list | `get_current_user` | DB user organization | Create verifies parent lead belongs to tenant; list filters activity tenant | Service regression tests added |
| `/lead-notes` create/list/delete | `get_current_user` | DB user organization | Parent lead check and tenant-filtered note reads/deletes | Service regression tests added |
| `/agent-memory` save/history/latest | `get_current_user` | DB user organization | Memory save sets tenant ID; reads filter tenant | Service regression tests added |
| `/users` list/get/role/status/delete | Owner/admin RBAC | DB user organization | All target-user reads scoped by both user ID and organization ID | Service read tests added; mutation route tests pending |
| `/invitations` create/list | Owner/manager/admin RBAC | DB user organization | Create uses caller organization; list filters organization | Source review; route tests pending |
| `/subscriptions/{organization_id}` | Owner/manager/admin; super-admin | DB user organization | Non-super-admin ID must equal caller organization | Source review; route tests pending |
| `/audit/logs`, `/audit/events` | Owner/manager/admin RBAC | DB user organization | Both queries filter organization ID | Service regression tests added |
| `/organization-dashboard` | `get_current_user` | DB user organization | Counts users, leads and invitations by tenant | Service regression test added |
| `/organizations` list/detail | Super-admin or tenant roles | DB user organization | Non-super-admin list/detail filters by tenant | Existing + new service tests |
| `/crm`, `/dashboard`, `/revenue-forecast`, `/executive-intelligence`, `/sales-agent/priorities`, `/relationship-intelligence` | `get_current_user` or feature gate wrapping it | DB user organization | Query services reviewed use organization filters | Source review; endpoint integration tests pending |
| `/osint`, `/intelligence`, `/technology`, `/business-discovery`, `/lead-qualification`, `/multi-agent`, `/opportunity`, `/reports` | `get_current_user` or feature gate wrapping it | DB user organization for quota/memory | Requests are not direct tenant record reads; AI usage logged against caller organization | Source review; output/egress tests pending |
| `/subscriptions` collection/create | Super-admin only | Explicit organization ID | Admin-only operation | Source review |
| `/auth/*` | Login/refresh/logout/change-password | User identity from credentials/session | Session version, refresh-JTI rotation and cookie Origin checks | Auth unit tests partial |
| `/invitations/accept` | Public, invitation token | Tenant bound to hashed invitation record | Token hash lookup, expiry/used check and email match | Source review; race/abuse tests pending |

## Cross-tenant regression tests added

`backend/tests/test_tenant_isolation_services.py` uses an isolated in-memory SQLite database with two organizations. It covers guessed organization, lead, note, activity, user, subscription, invitation and audit identifiers; write attempts through lead updates/deletes and note/activity creation; agent-memory history/latest; tenant dashboard counts; and ORM append-only audit rows.

These tests validate the service/query layer. They do **not** yet constitute a full HTTP endpoint matrix for every registered route. Route dependency overrides and role combinations must still be exercised in CI.

## Response-model controls

- `/leads` now uses `LeadResponse`.
- `/users` uses `UserManagementResponse`, which does not declare `hashed_password`.
- `/organizations`, `/subscriptions`, `/invitations`, `/activities`, `/lead-notes`, and `/audit/logs` already declare explicit response models.
- `/reports/generate` now returns a UUID report identifier, not the absolute server filesystem path.
- Several analytics/AI endpoints still return untyped dictionaries. They are not yet proven to exclude all future internal fields; response-model coverage remains an open hardening item.
- Invitation creation returns its one-time raw invitation token to the authorized creator. It is not returned by list endpoints; delivery/secret-handling policy needs a product decision before removing it from the create response.

## Residual concerns

- Full HTTP-level IDOR/RBAC tests are pending.
- Direct SQL/DB administrator access can bypass SQLAlchemy audit-log immutability events. Database privileges/append-only trigger or external audit sink are required for stronger tamper resistance.
- Application service account must not own the audit table or have UPDATE/DELETE privileges in production.
- Public API split across Vercel/Railway remains directly reachable at the Railway ingress, as described in `NETWORK_HARDENING.md`.
