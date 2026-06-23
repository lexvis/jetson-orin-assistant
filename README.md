# Jetson Orin Nano — Local GPU Inference Node (LLM + STT)

Infrastructure-as-code for an always-on **NVIDIA Jetson Orin Nano 8GB** (+ 500GB
NVMe) used as a single-purpose **GPU inference node**. It serves a local LLM and
speech-to-text on the GPU behind simple HTTP endpoints, for Home Assistant and a
separate mini-PC orchestrator to consume.

> Full step-by-step instructions: **[docs/Jetson-Orin-Nano-Assistant-Install-Guide.pdf](docs/Jetson-Orin-Nano-Assistant-Install-Guide.pdf)**

## Scope: the Jetson is inference-only
Only GPU models that run on the **llama.cpp / ggml** stack live on the Jetson.
Everything with side-effects or no GPU benefit runs on a **separate mini-PC**.

| Component | Host | Endpoint |
|---|---|---|
| LLM — Qwen3-8B Q4 (llama.cpp, native) | **Jetson GPU** | `:8080` OpenAI `/v1` |
| STT — Whisper large-v3-turbo Q5 (whisper.cpp, native) | **Jetson GPU** | `:8081` `/inference` |
| TTS — Piper | mini-PC / HA | Wyoming |
| Agent harness (OpenClaw), browser, approvals | mini-PC | — |
| Home Assistant (Assist pipeline) | HA host | — |

## Architecture
```
  Home Assistant (Assist)        mini-PC (orchestrator)
    |  STT audio                    |  chat / tools / approvals
    v                               v   (OpenClaw, Piper TTS, browser)
  Jetson Orin Nano 8GB  (LAN, no inbound router ports)
    - llama-server   :8080  -> OpenAI-compatible /v1   (Qwen3-8B)
    - whisper-server :8081  -> /inference (STT, auto NL/EN)
  systemd-managed, GPU-accelerated, auto-start on boot
```

## Key decisions
- **Install:** JetPack 7.2 "Jetson ISO" written to a USB stick installs Jetson
  Linux **directly onto the NVMe** (firmware capsule baked in) → remove USB → run
  fully from NVMe. No SD clone, no x86 Linux host. One-time DisplayPort monitor +
  USB keyboard for setup (no video over USB-C); headless via SSH after that.
- **Runtime:** **native builds, no Docker.** `llama.cpp` (LLM) and `whisper.cpp`
  (STT), both compiled for CUDA **sm_87** against the host CUDA 13.2, served as
  systemd services. On JP7 there is no current prebuilt dusty-nv image, and JP6
  CUDA images fail/segfault — native is the reliable path (and reclaims ~130MB).
- **Models:** Qwen3-8B Q4_K_M (text, `:8080`) and Whisper large-v3-turbo Q5_0
  (STT, auto NL/EN, `:8081`). See `versions.env`.
- **Lean + efficient:** headless `multi-user.target`, non-essential services
  disabled, **MAXN_SUPER persistent** with **DVFS left on** (no 24/7
  `jetson_clocks` — that just wastes energy), 16GB swap on NVMe.
- **Off-Jetson (mini-PC):** Piper TTS, the OpenClaw agent harness, browser
  automation, and the human-in-the-loop approval gates. Personalization via
  **RAG + memory** on the mini-PC, **not** finetuning on the Jetson.

## Layout
| Path | Purpose |
|------|---------|
| `docs/` | Installation guide (PDF) |
| `versions.env` | Pinned versions (edit deliberately) |
| `scripts/` | System minimisation, swap, JetPack USB-ISO install notes, PDF generator |
| `config/llamacpp/` | Model + server args, systemd unit notes |
| `config/homeassistant/` | Assist / Wyoming integration notes |
| `config/openclaw/` | OpenClaw config — **runs on the mini-PC, not the Jetson** |
| `wireguard/` | WG templates for off-site admin (no keys committed) |
| `compose/` | **Legacy** Docker stack from the pre-native plan (kept for reference) |
| `.env.example` | Secrets template — copy to `.env` (gitignored) |

## Getting started
1. Follow the PDF guide to flash + migrate to NVMe and minimise the system.
2. Install the minimal CUDA 13.2 build toolchain (`cuda-minimal-build-13-2`,
   `libcublas-dev-13-2`, `cmake`, `g++`).
3. Build & serve the LLM (`llama.cpp`, `:8080`) and STT (`whisper.cpp`, `:8081`)
   as systemd services — see the guide phases 4–5.
4. Point Home Assistant (Extended OpenAI Conversation) at `http://<jetson-ip>:8080/v1`.

## Security note
Never expose `:8080`/`:8081` to the internet — keep the Jetson on the LAN/VPN.
The agent harness, its approval gates, and the autonomy model live on the mini-PC;
see [`SECURITY.md`](SECURITY.md) and `config/openclaw/`. `.env`, real
`wireguard/*.conf`, `*.key`, and model weights are gitignored.
