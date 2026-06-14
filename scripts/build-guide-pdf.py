#!/usr/bin/env python3
"""Build the Jetson Orin Nano assistant installation guide PDF.

Usage:  python build-guide-pdf.py
Requires: fpdf2  (pip install fpdf2)
Outputs:  ../docs/Jetson-Orin-Nano-Assistant-Install-Guide.pdf
"""
import os
from datetime import date
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# ---- text sanitiser: keep core-font (latin-1) safe ----
_MAP = {
    "\u2192": "->", "\u2190": "<-", "\u2014": "-", "\u2013": "-",
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2026": "...", "\u2248": "~", "\u00d7": "x", "\u2022": "-",
    "\u26a0": "[!]", "\ufe0f": "", "\u2705": "[OK]", "\u274c": "[X]",
    "\U0001f99e": "", "\u00b7": "-", "\u2265": ">=", "\u2264": "<=",
}
def s(t):
    for k, v in _MAP.items():
        t = t.replace(k, v)
    return t.encode("latin-1", "ignore").decode("latin-1")

# ---- colors ----
INK = (33, 37, 41)
ACCENT = (10, 90, 160)
MUTED = (110, 110, 110)
CODEBG = (244, 244, 246)
WARNBG = (255, 244, 229)
SECBG = (230, 244, 235)

class Guide(FPDF):
    # Force every multi_cell to return the cursor to the left margin on the next
    # line. fpdf2 defaults to new_x=RIGHT, which left the X cursor at the right
    # margin so any following multi_cell (cover title, callout body) started off
    # the page and rendered clipped on the right edge.
    def multi_cell(self, *args, **kwargs):
        kwargs.setdefault("new_x", XPos.LMARGIN)
        kwargs.setdefault("new_y", YPos.NEXT)
        return super().multi_cell(*args, **kwargs)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 8, s("Jetson Orin Nano 8GB - Personal Assistant Install Guide"), align="L")
        self.cell(0, 8, s("p. %d" % self.page_no()), align="R")
        self.ln(10)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*MUTED)
        self.cell(0, 8, s("Generated %s - deployment repo: jetson-orin-assistant" % date.today().isoformat()), align="C")

pdf = Guide(format="A4")
pdf.set_auto_page_break(auto=True, margin=16)
pdf.set_margins(16, 16, 16)
W = pdf.w - 32  # effective width

def h1(t):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*ACCENT)
    pdf.multi_cell(W, 9, s(t))
    pdf.ln(2)
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(0.5)
    y = pdf.get_y()
    pdf.line(16, y, 16 + W, y)
    pdf.ln(4)
    pdf.set_text_color(*INK)

def h2(t):
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*ACCENT)
    pdf.multi_cell(W, 7, s(t))
    pdf.ln(1)
    pdf.set_text_color(*INK)

def h3(t):
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*INK)
    pdf.multi_cell(W, 6, s(t))

def body(t):
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(*INK)
    pdf.multi_cell(W, 5.6, s(t))
    pdf.ln(1)

def bullets(items):
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(*INK)
    for it in items:
        x = pdf.get_x()
        pdf.cell(5, 5.6, s("-"))
        pdf.multi_cell(W - 5, 5.6, s(it))
        pdf.set_x(x)
    pdf.ln(1)

def code(lines):
    pdf.set_font("Courier", "", 9)
    pdf.set_fill_color(*CODEBG)
    pdf.set_text_color(*INK)
    for ln in lines:
        pdf.cell(W, 5, s("  " + ln), fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

def callout(title, t, bg):
    pdf.set_fill_color(*bg)
    pdf.set_draw_color(*MUTED)
    x0, y0 = pdf.get_x(), pdf.get_y()
    pdf.set_font("Helvetica", "B", 10)
    pdf.multi_cell(W, 5.6, s(title), fill=True, border="LR")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(W, 5.6, s(t), fill=True, border="LRB")
    pdf.ln(2)

def kv_table(rows, headers, widths):
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_fill_color(*ACCENT)
    pdf.set_text_color(255, 255, 255)
    for hdr, wd in zip(headers, widths):
        pdf.cell(wd, 6.5, s(hdr), border=1, fill=True, align="L")
    pdf.ln()
    pdf.set_text_color(*INK)
    pdf.set_font("Helvetica", "", 9.5)
    fill = False
    for row in rows:
        pdf.set_fill_color(248, 248, 250)
        # compute row height by wrapping; simple single-line assumption per cell
        for val, wd in zip(row, widths):
            pdf.cell(wd, 6.2, s(val), border=1, fill=fill, align="L")
        pdf.ln()
        fill = not fill
    pdf.ln(2)

# ================= COVER =================
pdf.add_page()
pdf.ln(28)
pdf.set_font("Helvetica", "B", 26)
pdf.set_text_color(*ACCENT)
pdf.multi_cell(W, 11, s("NVIDIA Jetson Orin Nano 8GB"))
pdf.set_font("Helvetica", "B", 17)
pdf.set_text_color(*INK)
pdf.multi_cell(W, 9, s("Local Multimodal Personal Assistant"))
pdf.ln(2)
pdf.set_font("Helvetica", "", 12)
pdf.set_text_color(*MUTED)
pdf.multi_cell(W, 6, s("Installation guide: boot to NVMe, local + cloud models, voice, Home Assistant, and the OpenClaw agent harness - secured, outbound-only, with human-in-the-loop approval."))
pdf.ln(8)
pdf.set_draw_color(*ACCENT); pdf.set_line_width(0.4)
pdf.line(16, pdf.get_y(), 16 + W, pdf.get_y()); pdf.ln(6)
pdf.set_font("Helvetica", "B", 11); pdf.set_text_color(*INK)
pdf.multi_cell(W, 6, s("Key decisions captured in this build"))
pdf.set_font("Helvetica", "", 10.5); pdf.set_text_color(*INK)
for it in [
    "Boot: SD card as throwaway bootstrap media -> clone rootfs to NVMe -> run from NVMe (no x86 Linux host).",
    "Local runtime: llama.cpp llama-server (OpenAI-compatible), 3-4B Q4 multimodal model.",
    "Optional cloud offload: GitHub Copilot provider, latest Claude Opus as preferred model.",
    "Agent harness: OpenClaw (sandboxed), WhatsApp Cloud API channel, admin via WireGuard.",
    "Security: outbound-only (no inbound ports), DM pairing, no payment credentials, explicit approval for high-impact actions.",
]:
    x = pdf.get_x(); pdf.cell(5, 5.6, s("-")); pdf.multi_cell(W - 5, 5.6, s(it)); pdf.set_x(x)
pdf.ln(6)
pdf.set_font("Helvetica", "I", 9); pdf.set_text_color(*MUTED)
pdf.multi_cell(W, 5, s("Version %s - generated %s. Pin versions in versions.env; treat this as living documentation." % ("1.0", date.today().isoformat())))

# ================= 1. OVERVIEW =================
h1("1. Overview & Architecture")
body("This guide builds an always-on home assistant on a Jetson Orin Nano 8GB with a 500GB NVMe SSD. It serves a frequently-updated multimodal model behind an OpenAI-compatible endpoint and layers the OpenClaw agent harness on top, with strong security defaults.")
h2("Components")
bullets([
    "llama.cpp (llama-server): local OpenAI-compatible inference for a 3-4B quantized vision model.",
    "GitHub Copilot provider (optional): cloud models (Claude Opus) to offload the Jetson for heavy reasoning.",
    "Open WebUI: browser chat interface.",
    "Wyoming Whisper (STT) + Piper (TTS): voice, integrated with Home Assistant Assist.",
    "OpenClaw: agentic harness (skills, browser, messaging) running sandboxed.",
    "WireGuard + VPS: outbound-only admin access and WhatsApp webhook relay.",
])
h2("Architecture (data flow)")
code([
    "WhatsApp Cloud API --> VPS (webhook + WireGuard server)",
    "                          |  (relayed over WireGuard tunnel)",
    "                          v",
    "  Jetson Orin Nano 8GB (outbound-only; no inbound router ports)",
    "    - llama-server  :8080  -> OpenAI /v1 (local model)",
    "    - Open WebUI    :3000",
    "    - Whisper :10300  Piper :10200  -> Home Assistant Assist",
    "    - OpenClaw Gateway (sandboxed)",
    "        primary  = github-copilot/claude-opus-4.8  (cloud)",
    "        fallback = llamacpp/<local model>          (offline)",
])
h2("Design principles")
bullets([
    "Outbound-only: the device initiates all connections; no inbound ports on the home network.",
    "Approval gates: high-impact actions (orders, payments) require explicit human confirmation.",
    "Least privilege: the agent holds no payment/order credentials; sandboxed tool execution.",
    "Version pinning: reproducible deployment via versions.env; avoid 'latest' in production.",
])

# ================= 2. HARDWARE =================
h1("2. Hardware Checklist & Memory Budget")
h2("Hardware")
bullets([
    "Jetson Orin Nano 8GB Developer Kit (Super-capable; JetPack 6.2).",
    "NVMe M.2 SSD 500GB (PCIe Gen3) installed in the M.2 Key-M slot.",
    "microSD card (>=64GB) used only for bootstrap.",
    "Active cooling (fan) - required for sustained inference.",
    "12V DC barrel power supply that can sustain MAXN SUPER (do not rely on weak USB-C PD).",
    "Ethernet (recommended) for a stable headless server.",
])
h2("Memory budget (8GB unified - plan carefully)")
kv_table(
    rows=[
        ["OS (headless)", "~1.5 GB"],
        ["Local model (3-4B Q4)", "3-4 GB"],
        ["Whisper (base)", "0.5-1 GB"],
        ["Piper (TTS)", "<0.2 GB"],
        ["Open WebUI", "~0.3 GB"],
        ["OpenClaw (Node)", "0.3-0.5 GB"],
        ["Chromium (browser, on-demand)", "0.5-1.5 GB"],
    ],
    headers=["Component", "Approx. RAM"],
    widths=[120, 58],
)
callout("[!] 8GB is the hard constraint",
        "Everything active at once exceeds 8GB. Use a 3-4B local model (not 7B), run Chromium on-demand only, keep 8-16GB swap on NVMe, and prefer the cloud (Copilot) model for heavy work. Serialize peaks (voice OR browser-agent, not both).",
        WARNBG)

# ================= 3. BOOTSTRAP =================
h1("3. Phase 1 - Bootstrap to NVMe")
body("The Jetson boots via a Tegra bootloader in QSPI flash on the module, so Windows imaging tools cannot make an SSD bootable on their own. Use the SD card as throwaway bootstrap media, then clone the OS to the NVMe and remove the SD. No x86 Linux host required.")
h2("Steps")
body("1) Flash the JetPack 6.2 SD image on Windows with balenaEtcher. 2) Boot once from SD and finish first-boot setup. 3) Update firmware (QSPI) and enable NVMe boot from the Jetson itself:")
code([
    "sudo apt update && sudo apt full-upgrade -y   # updates nvidia-l4t-bootloader",
    "sudo reboot",
])
body("4) Clone rootfs SD -> NVMe with the JetsonHacks scripts (run on the Jetson):")
code([
    "git clone https://github.com/jetsonhacks/rootOnNVMe.git",
    "cd rootOnNVMe && ./copy-rootfs-ssd.sh && ./setup-service.sh",
])
body("5) Set NVMe first in the UEFI boot order if needed. 6) Shut down, remove the SD, and boot - the system now runs entirely from the NVMe.")
callout("Note",
        "Dev kits that shipped with JetPack 5.x firmware need the apt firmware update before a JP6 SD image / NVMe boot works. The only pure-NVMe flash without a clone step is NVIDIA SDK Manager, which requires an x86 Linux host - intentionally avoided here.",
        SECBG)

# ================= 4. SYSTEM CONFIG =================
h1("4. Phase 2 - System Configuration")
body("Run on the device after booting from NVMe. See scripts/01-system-config.sh and scripts/02-swap.sh in the repo.")
h2("Power, cooling, headless")
code([
    "sudo nvpmodel -m 0        # MAXN SUPER",
    "sudo jetson_clocks        # max clocks",
    "sudo systemctl set-default multi-user.target   # disable desktop GUI (frees RAM)",
])
h2("Base packages + Node 24 (for OpenClaw)")
code([
    "sudo apt install -y build-essential git cmake curl ca-certificates",
    "curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -",
    "sudo apt install -y nodejs",
])
h2("Swap on NVMe (OOM safety net)")
code([
    "./scripts/02-swap.sh 12     # creates /mnt/nvme/swapfile, swappiness=10",
])
bullets([
    "Static IP or DHCP reservation for a stable headless server.",
    "SSH is enabled by default on JetPack; manage everything remotely.",
])

# ================= 5. DOCKER =================
h1("5. Phase 3 - Docker & jetson-containers")
body("JetPack ships Docker with the NVIDIA container runtime. Prefer prebuilt Jetson images (dustynv / jetson-containers) over building CUDA from source.")
code([
    "docker info | grep -i runtime          # confirm 'nvidia' runtime",
    "git clone https://github.com/dusty-nv/jetson-containers",
    "bash jetson-containers/install.sh",
])
callout("Tip",
        "Keep all model weights and Docker data on the NVMe (e.g. /mnt/nvme). Pin image tags in versions.env.",
        SECBG)

# ================= 6. LLAMA.CPP =================
h1("6. Phase 4 - Local Inference (llama.cpp)")
body("llama-server provides an OpenAI-compatible /v1 API for the local multimodal model (privacy/offline fallback). For vision you need the model GGUF and its matching --mmproj projector.")
h2("Model choice (balance)")
bullets([
    "Gemma 3 4B (Q4_K_M) + mmproj, or Qwen2.5-VL 3B (Q4) + mmproj.",
    "Download GGUF from a trusted source; verify checksums; pin the filename.",
    "Store under /mnt/nvme/models.",
])
h2("Run (see compose/docker-compose.yml)")
code([
    "llama-server -m /models/gemma-3-4b-it-Q4_K_M.gguf \\",
    "  --mmproj /models/gemma-3-4b-mmproj.gguf \\",
    "  --host 0.0.0.0 --port 8080 -ngl 99 --ctx-size 4096",
    "",
    "curl http://127.0.0.1:8080/v1/models   # health check",
])

# ================= 7. OPEN WEBUI =================
h1("7. Phase 5 - Open WebUI")
body("A browser chat UI pointed at the local endpoint. Brought up by docker-compose.")
code([
    "# environment (compose):",
    "OPENAI_API_BASE_URL=http://llamacpp:8080/v1",
    "OPENAI_API_KEY=sk-no-key-required",
    "# UI on http://<jetson-ip>:3000",
])
callout("Security", "Bind UI/endpoint ports to localhost or the WireGuard interface in production - do not expose them to the LAN/internet directly.", WARNBG)

# ================= 8. VOICE =================
h1("8. Phase 6 - Voice (Whisper + Piper)")
body("Wyoming services provide speech-to-text and text-to-speech that Home Assistant Assist can discover.")
code([
    "wyoming-whisper  --model base  --language nl   # :10300",
    "wyoming-piper    --voice nl_NL-mls-medium      # :10200",
])
bullets([
    "Load Whisper base/tiny and on-demand to conserve the 8GB budget.",
    "Both run as containers in docker-compose.yml.",
])

# ================= 9. HOME ASSISTANT =================
h1("9. Phase 7 - Home Assistant Assist")
bullets([
    "Add Wyoming integrations in HA pointing at <jetson-ip>:10300 (Whisper) and :10200 (Piper).",
    "Create an Assist pipeline: Whisper (STT) -> Conversation agent (LLM) -> Piper (TTS).",
    "For the LLM, use the Extended OpenAI Conversation custom integration (HACS) so you can set a custom base_url to http://<jetson-ip>:8080/v1.",
])
callout("Approval boundary", "HA voice must not trigger high-impact agent actions (orders/payments) without the OpenClaw approval gate. Keep HA on the LAN/WireGuard network only.", WARNBG)

# ================= 10. CONNECTIVITY =================
h1("10. Phase 8 - Connectivity (Outbound-only)")
body("No inbound ports on the home network. The Jetson dials out; interaction returns over the established connections.")
h2("Admin: WireGuard")
bullets([
    "Run a WG client on the Jetson that dials a WG server on your VPS.",
    "You reach the Jetson over the private tunnel; the home router opens no ports.",
    "Keep PersistentKeepalive=25 on the Jetson side. See wireguard/ in the repo.",
])
h2("Agent channel: WhatsApp Cloud API")
bullets([
    "The official Cloud API delivers inbound messages via a webhook (inbound by nature).",
    "Host the webhook receiver on the VPS, verify the Meta signature, and relay to the Jetson over WireGuard.",
    "Result: the Jetson / home network opens no inbound ports.",
])

# ================= 11. OPENCLAW =================
h1("11. Phase 9 - OpenClaw Agent Harness")
body("OpenClaw (github.com/openclaw/openclaw, MIT) is a self-hosted personal assistant that bridges chat apps to LLMs with skills, browser control and shell access. Microsoft's 'Scout' is built on OpenClaw. Runtime: Node 24.")
h2("Install (pin a version; do not blind-curl)")
code([
    "npm install -g openclaw@latest",
    "openclaw onboard --install-daemon     # installs the Gateway systemd service",
    "openclaw gateway status",
])
h2("Security configuration (NOT the defaults)")
callout("[!] Default = full host access for the main session",
        "You must override this. Sandbox non-main sessions (Docker), keep sandbox egress off (network: none), require pairing for unknown senders, and never enable tools.elevated (it bypasses the sandbox).",
        WARNBG)
code([
    "# config/openclaw/config.json5 (excerpt)",
    "agents.defaults.sandbox = {",
    "  mode: 'non-main', backend: 'docker', scope: 'session',",
    "  docker: { network: 'none' },     # no egress for sandboxed shell/code",
    "}",
    "tools = { profile: 'coding', alsoAllow: ['browser'] }  # capable + browser on",
    "browser = { enabled: true }        # isolated 'openclaw' profile (see below)",
    "logging = { redactSensitive: 'tools' }",
    "channels.whatsapp.dmPolicy = 'pairing'",
    "openclaw pairing approve whatsapp <code>   # approve a sender",
])
h2("The browser is enabled - but isolated")
bullets([
    "The agent uses a separate 'openclaw' browser profile, NOT your personal browser.",
    "That profile has no logged-in webshops and no saved payment methods, so the agent can browse and verify freely but cannot complete a purchase with your cards.",
    "Do not switch the agent to the 'user' profile (your real signed-in Chrome).",
])
bullets([
    "Give OpenClaw NO payment/order credentials (it can draft an order; you execute it).",
    "Run 'openclaw security audit' (add --deep / --fix) after any config or exposure change.",
    "Read the official 'Gateway exposure runbook' before any remote exposure.",
    "ARM64: Node + Playwright/Chromium work; watch for x86-assuming skills.",
])

# ================= 12. COPILOT OFFLOAD =================
h1("12. Phase 10 - Optional: GitHub Copilot Cloud Offload")
body("Offload heavy reasoning to cloud models via your GitHub Copilot subscription, keeping the local model as an offline/private fallback. This relaxes the 8GB pressure. OpenClaw supports a github-copilot/* provider natively.")
h2("Install the Copilot SDK harness plugin")
code([
    "openclaw plugins install @openclaw/copilot   # ~260MB incl. CLI binary",
    "# verify the linux-arm64 Copilot CLI binary loads on the Jetson:",
    "openclaw doctor",
])
h2("Preferred model = latest Claude Opus")
code([
    "// config/openclaw/config.json5 (excerpt)",
    "agents.defaults.model = {",
    "  primary: 'github-copilot/claude-opus-4.8',   // confirm id: openclaw models list",
    "  fallbacks: ['llamacpp/gemma-3-4b']",
    "}",
    "models: {",
    "  'github-copilot/claude-opus-4.8': { agentRuntime: { id: 'copilot' } },",
    "  aliases: { 'mijn-default': 'github-copilot/claude-opus-4.8' }",
    "}",
])
h2("Choosing your model (three levels)")
bullets([
    "Config: agents.defaults.model.primary + fallbacks (persistent default).",
    "CLI: openclaw models list / set, plus aliases.",
    "In chat: /model picker (per-session, pinned).",
])

# ================= 13. SECURITY =================
h1("13. Security Model & Approval Gates")
body("Principle: maximise useful autonomy, minimise blast radius. The assistant should resolve the routine 95% on its own and stop only for the consequential 5%. It must do a genuine check-in for sensitive actions - and never try to force, retry around, or social-engineer its way past a denied/pending approval.")
h2("Autonomy tiers")
bullets([
    "Tier A - Autonomous (no prompt): search, browse (isolated profile), summarise, draft replies, run code in the sandbox, install Python/npm packages in the sandbox, read Home Assistant sensors, manage its own workspace files.",
    "Tier B - Act + notify: reversible local changes and non-critical home control (e.g. lights); the agent acts and tells you what it did.",
    "Tier C - Approval required (hard stop): spending money, orders/purchases/payments, messaging or emailing third parties on your behalf, posting publicly, deleting data irreversibly, changing credentials/security, controlling critical devices, or running outside the sandbox.",
])
h2("Why a denied approval actually holds")
bullets([
    "Least privilege: the agent holds NO payment/order credentials, so a Tier C action cannot physically complete without you - the gate is structural, not just a prompt instruction.",
    "Isolated browser profile: no saved cards or logged-in webshops, so 'just check out on the site' is not possible.",
    "Sandbox with no egress (network: none) for shell/code; tools.elevated stays off.",
    "The agent is instructed to surface the blocker and wait, not to brute-force or seek a workaround.",
])
h2("Controls in this build")
bullets([
    "Outbound-only networking; no inbound router ports (WireGuard + VPS relay).",
    "OpenClaw sandboxed (Docker), sandbox egress network: none, DM pairing on.",
    "Browser enabled but isolated ('openclaw' profile) - capable yet credential-free.",
    "No payment/order credentials available to the agent (it drafts; you execute).",
    "Secrets in .env (gitignored); WireGuard private keys generated on-device.",
    "Audit: run 'openclaw security audit' (--deep/--fix) and 'openclaw doctor'; keep redacted logs (logging.redactSensitive: 'tools').",
])
callout("Golden rule",
        "Agents must never place orders or take consequential actions without explicit prior approval - and must never try to force or bypass that approval. Enforced by least privilege (no credentials) + sandbox + isolated browser, not by prompt instructions alone.",
        SECBG)
h2("Borrowed from Microsoft Scout & recognised frameworks")
bullets([
    "Scout identity/SSO -> personal analog: strict DM pairing + allowlists (only you can drive the bot); one trusted operator per gateway.",
    "Scout policy/governance -> tool allowlists + autonomy tiers + 'openclaw security audit --fix' (flips open policies to allowlists).",
    "Scout audit/observability -> redacted tool logs + periodic audit/doctor runs.",
    "OWASP LLM/Agentic Top 10 -> mitigate excessive agency (least privilege + approval) and prompt injection (treat inbound DMs AND web page content as untrusted).",
    "NIST AI RMF + least-privilege/egress control -> sandbox network: none, no inbound ports, deliberate version pinning.",
])

# ================= 14. VERIFY =================
h1("14. Verification & Benchmarking")
code([
    "lsblk                              # root on nvme0n1p1",
    "nvpmodel -q                        # MAXN SUPER",
    "curl http://127.0.0.1:8080/v1/models",
    "docker compose ps                  # all services up",
    "openclaw gateway status",
    "# quick local inference latency:",
    "time curl -s http://127.0.0.1:8080/v1/chat/completions \\",
    "  -H 'Content-Type: application/json' \\",
    "  -d '{\"model\":\"local\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}]}'",
])

# ================= 15. MAINTENANCE =================
h1("15. Maintenance & Updates")
bullets([
    "Update models: download a new GGUF, update the filename in compose + versions.env, restart llamacpp.",
    "Update OpenClaw: npm update -g openclaw (then 'openclaw doctor'); pin the version in versions.env.",
    "Update containers: bump tags in versions.env deliberately, then docker compose pull && up -d.",
    "Keep the OS current: sudo apt update && sudo apt full-upgrade (includes firmware).",
    "Commit every change to the deployment repo so the running state is captured.",
])

# ================= 16. TROUBLESHOOTING =================
h1("16. Troubleshooting")
kv_table(
    rows=[
        ["NVMe won't boot after clone", "Update firmware (apt full-upgrade), check UEFI boot order"],
        ["OOM / killed processes", "Use 3-4B model, add swap, run Chromium on-demand"],
        ["pip install torch broken", "Use Jetson-specific wheels / jetson-containers, not default pip"],
        ["Copilot runtime missing", "openclaw plugins install @openclaw/copilot; openclaw doctor"],
        ["WhatsApp not receiving", "Check VPS webhook + Meta signature + WireGuard tunnel"],
        ["Solcast/secrets empty", "Secrets in .env, never committed; check env_file mapping"],
    ],
    headers=["Symptom", "Fix"],
    widths=[70, 108],
)

# ================= 17. APPENDIX =================
h1("Appendix - Version Pin Table")
body("Mirror of versions.env. Update deliberately; verify on-device before bumping.")
kv_table(
    rows=[
        ["JetPack", "6.2"],
        ["L4T", "r36.4"],
        ["llama.cpp image", "dustynv/llama_cpp:r36.4.0"],
        ["Open WebUI", "ghcr.io/open-webui/open-webui:main"],
        ["Wyoming Whisper", "rhasspy/wyoming-whisper"],
        ["Wyoming Piper", "rhasspy/wyoming-piper"],
        ["Node", "24"],
        ["OpenClaw", "pin once chosen"],
        ["Cloud model", "github-copilot/claude-opus-4.8"],
        ["Local model", "llamacpp/gemma-3-4b (Q4)"],
    ],
    headers=["Item", "Pinned value"],
    widths=[80, 98],
)

out_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
os.makedirs(out_dir, exist_ok=True)
out = os.path.normpath(os.path.join(out_dir, "Jetson-Orin-Nano-Assistant-Install-Guide.pdf"))
pdf.output(out)
print("Wrote:", out)
