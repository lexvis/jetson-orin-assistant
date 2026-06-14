# Jetson Orin Nano — Local Multimodal Personal Assistant (Deployment)

Infrastructure-as-code for an always-on home personal assistant on an
**NVIDIA Jetson Orin Nano 8GB** (+ 500GB NVMe), serving a frequently-updated
multimodal model behind an OpenAI-compatible endpoint, with an
[OpenClaw](https://github.com/openclaw/openclaw) agent layer.

> Full step-by-step instructions: **[docs/Jetson-Orin-Nano-Assistant-Install-Guide.pdf](docs/Jetson-Orin-Nano-Assistant-Install-Guide.pdf)**

## Architecture

```
                 (outbound only — no inbound ports on home network)
  WhatsApp Cloud API ──► VPS (webhook + WireGuard server) ──WG tunnel──► Jetson
                                                                          │
  Jetson (8GB):                                                           ▼
   ├─ llama.cpp llama-server   → OpenAI-compatible /v1 (local model)
   ├─ Open WebUI               → chat UI
   ├─ Wyoming Whisper (STT) + Piper (TTS)  → Home Assistant Assist
   └─ OpenClaw (Gateway, sandboxed)  → agent harness
         primary  = github-copilot/claude-opus-4.8  (cloud, offloads Jetson)
         fallback = llamacpp/<local model>          (offline / private)
```

## Key decisions
- **Boot:** SD card as throwaway bootstrap media → clone rootfs to NVMe
  (`rootOnNVMe`) → remove SD → run fully from NVMe. No Linux host needed.
- **Runtime:** llama.cpp `llama-server` (not Ollama).
- **Model:** local 3–4B Q4 (balance) + optional GitHub Copilot cloud offload
  (Opus primary). See `versions.env`.
- **Connectivity:** outbound only. Admin via **WireGuard**; agent via **WhatsApp
  Cloud API** with the webhook on the VPS, relayed over WireGuard.
- **Security & autonomy:** the assistant is highly autonomous for routine,
  reversible work and only does an **explicit human check-in for high-impact
  actions** (payments, orders, messaging third parties, deleting data). OpenClaw
  runs **sandboxed** (`sandbox.mode: "non-main"`, sandbox egress `network: "none"`);
  the agent's **browser is enabled but isolated** (separate `openclaw` profile, no
  saved logins/payments). **DM pairing** on, **no payment/order credentials**, and
  it must never work around a pending/denied approval. Run `openclaw security audit`.

## Layout
| Path | Purpose |
|------|---------|
| `docs/` | Installation guide (PDF) |
| `versions.env` | Pinned versions (edit deliberately) |
| `scripts/` | System config, swap, NVMe migration notes |
| `compose/` | Docker Compose for the stack |
| `config/openclaw/` | OpenClaw config (models, sandbox, channels) |
| `config/llamacpp/` | Model + server args |
| `config/homeassistant/` | Assist / Wyoming integration notes |
| `wireguard/` | WG templates (no keys committed) |
| `.env.example` | Secrets template — copy to `.env` (gitignored) |

## Getting started
1. Follow the PDF guide to flash + migrate to NVMe and configure the system.
2. `cp .env.example .env` and fill in secrets (never commit `.env`).
3. Bring up the stack: `docker compose -f compose/docker-compose.yml up -d`.
4. Onboard OpenClaw: `openclaw onboard --install-daemon` (Node 24).

## Security note
Never commit secrets. `.env`, `wireguard/*.conf` (real), `*.key`, and model
weights are gitignored. Review OpenClaw's "Gateway exposure runbook" before any
remote exposure. See [`SECURITY.md`](SECURITY.md) for the full autonomy/approval
model and the controls borrowed from Microsoft Scout and OWASP/NIST.
