# Attack Surface Review — Phase 2

Scope: source review of the current security-hardening branch and registered FastAPI router families. Search-index checks against the default branch found no dangerouslySetInnerHTML, UploadFile, FileResponse, SQL text()/execute(), or OpenAI/Anthropic/LangChain/Ollama references. These searches are useful indicators, not proof that no equivalent behavior exists under another name.

## Input and query handling

- Public domain input is normalized/validated through IDNA and rejected if it is an IP literal, localhost, or an internal/test suffix.
- Outbound HTTPS resolves and validates all DNS answers, connects to a pinned public IP, preserves TLS SNI/certificate validation against the hostname, disables automatic redirects, and validates each redirect target before connecting.
- The get_ssl_info path also connects to a pinned validated address while verifying the original hostname.
- DNS A-record lookups reject non-global results.
- SQLAlchemy ORM queries use bound parameters for reviewed tenant-sensitive access paths. No raw SQL construction was found in the reviewed services.
- Pydantic request schemas now bound many high-risk strings and reject unexpected fields for organization, lead, activity, note, invitation, subscription, login, password and sales-agent inputs.
- Nginx caps hosted request bodies at 10 MB. Direct Railway ingress body-size enforcement remains dependent on platform edge limits; the application has not yet added a complete streaming ASGI body cap.

## File handling

No upload route or file-response/download route was found in the registered API router inventory or the default-branch code search. The report generator writes server-side PDF files using UUID-derived names and returns only the report identifier. There is no public report download endpoint in this branch. If uploads are added later, enforce content-type sniffing, extension allowlists, file-size limits, malware scanning, random storage names, storage outside the web root and tenant-bound download authorization.

## XSS and output handling

- React's standard rendering escapes text by default; no dangerouslySetInnerHTML match was found in the repository's default-branch search.
- PDF report text and recommendation strings are HTML-escaped before ReportLab Paragraph rendering.
- The frontend CSP is nonce-based for scripts and denies object embedding and framing. Inline style attributes remain allowed as a compatibility exception for current animation/UI styles.
- A browser-based XSS regression suite and CSP report-only rollout have not been run.

## LLM / prompt-injection surface

No live LLM provider SDK, API endpoint, or LangChain/Ollama integration was found in the reviewed repository search. The current multi-agent orchestration is deterministic function composition, not an autonomous model/tool agent. There is therefore no currently evidenced model prompt/tool execution path to test for prompt injection or model-mediated data exfiltration. If a hosted LLM or agent tool is introduced, treat all domain content, scraped HTML, emails, documents and user-provided notes as untrusted; keep tenant authorization outside the model; use allowlisted tools with server-side tenant checks; redact sensitive context; prohibit arbitrary URL/file access; and test prompt injection, cross-tenant retrieval and tool exfiltration before release.

## Remaining SSRF and egress risk

DNS pinning closes the ordinary DNS-rebinding gap for the shared HTTPS fetch helper and TLS inspection path. The WHOIS library and DNS resolver perform separate outbound network operations and require an environment-level egress policy. Hosted production must deny private, loopback, link-local, multicast, reserved and cloud metadata ranges at the network boundary. The self-hosted Compose network currently has general outbound access; host firewall/egress filtering is still an operator requirement. Do not treat application DNS checks as the only SSRF control.

## Audit and tamper resistance

Sensitive lead, note, activity, invitation, organization, subscription and AI usage actions are attributed to the authenticated actor in audit events where those route/service paths have been wired. User role/status/delete changes already log audit events. ORM event hooks reject audit row updates/deletes; PostgreSQL trigger and DB-role restrictions are supplied in backend/sql/audit_log_hardening.sql but must be applied by a DBA. A superuser can still bypass/disable them; use an external append-only sink/SIEM for stronger evidence.
