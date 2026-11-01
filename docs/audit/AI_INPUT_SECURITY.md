# AI, Untrusted Input and External Data Security

## Current implementation boundary

The current dependency inventory and source review show no external hosted LLM SDK or direct LLM-provider API client. The multi-agent workflow in `backend/app/services/multi_agent_service.py` is deterministic service orchestration rather than an autonomous model with unrestricted tools. Therefore, classic model prompt injection and model-driven tool exfiltration are not currently evidenced as an active runtime path.

The application does accept user-supplied domains, business fields, notes and stored analysis data. Treat all of these as untrusted input. Domain analysis performs outbound network requests, so SSRF remains a relevant attack surface even without an LLM.

## Controls currently present

- Domain strings are normalized/validated by `backend/app/core/input_validation.py`.
- `backend/app/core/safe_http.py` rejects non-public DNS answers, pins outbound HTTPS connections to a validated IP while preserving hostname SNI/certificate verification, restricts to HTTPS, manually validates each redirect and limits redirect count/timeouts.
- Report filenames are generated from random identifiers, not user-controlled domain strings.
- PDF text is HTML-escaped before it is rendered by ReportLab.
- Pydantic request models reject unexpected fields and constrain lengths/ranges on lead, note, activity, invitation, report and agent-memory endpoints.
- React renders ordinary text as escaped content; a source review found no use of `dangerouslySetInnerHTML`, `.innerHTML`, or `.outerHTML` in the reviewed frontend source.
- The frontend CSP uses a per-request nonce for scripts and disallows `unsafe-inline` in `script-src`.

## SSRF residual risk

The shared HTTPS fetch and TLS-inspection paths connect to a pinned public IP selected from validated DNS answers, preventing the ordinary DNS-rebinding race for those paths. The WHOIS library and DNS resolver still perform separate outbound operations. Production must enforce outbound egress policy at the network layer:
- Deny loopback, private, link-local, multicast, reserved and cloud metadata ranges for IPv4 and IPv6.
- Permit outbound TCP 443 only where required; block direct access to metadata endpoints and internal control planes.
- Apply the same restrictions to WHOIS, DNS, TLS inspection and all future integrations.
- Retain the pinned-IP outbound HTTP transport with preserved Host/SNI and certificate validation; add network egress filtering for WHOIS/DNS and any future outbound integration.

This risk is not represented as fully solved by application DNS validation alone.

## Requirements before any LLM provider is introduced

1. Keep tenant identity and authorization server-side; never trust tenant IDs embedded in prompts or model output.
2. Do not send secrets, JWTs, database URLs, credentials, or another tenant's records to a model.
3. Label retrieved web pages, emails, documents and user content as untrusted data; never treat their instructions as system/developer policy.
4. Use an allowlist of typed tools with server-side authorization and tenant checks on every invocation. Do not expose shell, arbitrary HTTP, database SQL or unrestricted filesystem tools.
5. Validate model outputs against strict Pydantic schemas and reject unexpected fields.
6. Keep tool credentials server-side and scoped to the minimum tenant/resource needed.
7. Require human approval for external side effects, financial operations, user invitations, exports and destructive actions.
8. Log model/tool metadata without prompt bodies, credentials or PII; apply redaction before logs leave the process.
9. Test prompt-injection attempts that request cross-tenant records, hidden system instructions, credential disclosure, arbitrary URL fetches, tool escalation and output-schema bypass.
10. Keep retrieval indexes, caches and vector stores tenant-partitioned; test cross-tenant retrieval with guessed IDs and adversarial metadata.

## Uploads and browser rendering

No backend file-upload endpoint (`UploadFile`/multipart file handler) is currently present. A future upload feature must add size limits, MIME allowlists, magic-byte validation, malware scanning, randomized storage keys, non-executable storage, authorization on download, and tenant-isolated object storage before release.

Frontend source reviewed to date uses normal React rendering and does not use raw HTML injection APIs. Continue enforcing the static XSS test in CI; any exception must have a sanitizer and security review.
