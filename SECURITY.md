# Security & Autonomy Model

Goal: **maximise useful autonomy, minimise blast radius.** The assistant should
resolve the routine ~95% of tasks on its own and stop only for the consequential
~5%. For sensitive actions it does a genuine human check-in — and it must **never
try to force, retry around, or social-engineer past a denied/pending approval.**

## Autonomy tiers

| Tier | Examples | Behaviour |
|------|----------|-----------|
| **A — Autonomous** | search, browse (isolated profile), summarise, draft replies, run code in the sandbox, install Python/npm packages in the sandbox, read Home Assistant sensors, manage its own workspace files | Runs without prompting |
| **B — Act + notify** | reversible local changes, non-critical home control (e.g. lights) | Acts, then tells you what it did |
| **C — Approval required (hard stop)** | spending money, orders/purchases/payments, messaging or emailing third parties on your behalf, posting publicly, deleting data irreversibly, changing credentials/security, controlling critical devices, running outside the sandbox | Pauses and waits for explicit approval |

## Why a denied approval actually holds

The gate is **structural, not just a prompt instruction**:

- **Least privilege** — the agent holds **no payment/order credentials**, so a
  Tier C action cannot physically complete without you.
- **Isolated browser** — the agent uses a separate `openclaw` Chrome profile with
  **no saved cards and no logged-in webshops**, so "just check out on the site" is
  impossible. Never switch the agent to the `user` (real signed-in) profile.
- **Sandbox with no egress** — non-main sessions run in Docker with
  `sandbox.docker.network: "none"`; `tools.elevated` stays off (it would bypass
  the sandbox).
- The agent is instructed to **surface the blocker and wait**, not to brute-force
  or seek a workaround.

## Controls in this build

- Outbound-only networking; no inbound router ports (WireGuard + VPS relay).
- OpenClaw sandboxed (Docker), sandbox egress `network: "none"`, DM pairing on.
- Browser **enabled but isolated** (`openclaw` profile) — capable yet credential-free.
- No payment/order credentials available to the agent (it drafts; you execute).
- Secrets in `.env` (gitignored); WireGuard private keys generated on-device.
- `logging.redactSensitive: "tools"` keeps secrets out of logs.
- Run `openclaw security audit` (`--deep` / `--fix`) and `openclaw doctor` after
  any config or exposure change.

## Borrowed from Microsoft Scout & recognised frameworks

| Source | Concept | Personal-scale control here |
|--------|---------|------------------------------|
| **Scout** | Identity / SSO (Entra) | Strict **DM pairing + allowlists**; one trusted operator per gateway |
| **Scout** | Policy / governance | Tool allowlists + autonomy tiers + `openclaw security audit --fix` |
| **Scout** | Audit / observability | Redacted tool logs + periodic `security audit` / `doctor` |
| **OWASP LLM / Agentic Top 10** | Excessive agency | Least privilege + approval gate |
| **OWASP LLM / Agentic Top 10** | Prompt injection | Treat inbound DMs **and** fetched web content as untrusted |
| **NIST AI RMF** | Govern / map / measure / manage | Periodic audits, deliberate version pinning |
| Least-privilege / egress control | Network segmentation | Sandbox `network: "none"`, no inbound ports |

## Operating checklist

1. `openclaw security audit --deep` — review and resolve flagged footguns.
2. Keep `tools.elevated` unset; keep the agent on the isolated browser profile.
3. Verify no payment/order credentials are reachable by the agent.
4. Re-run the audit after every config change or before exposing anything remotely.
