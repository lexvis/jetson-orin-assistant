# Home Assistant integration (Assist + Voice)

Connect HA's **Assist** pipeline to the Jetson inference node. The Jetson serves
the **LLM** (`:8080`) and **STT** (`:8081`); **TTS (Piper)** and the agent run
off-Jetson (mini-PC / HA add-on).

## Conversation agent (LLM)
Point HA at the Jetson's OpenAI-compatible endpoint:
- `http://<jetson-ip>:8080/v1` (llama-server, Qwen3-8B).
- Use the **Extended OpenAI Conversation** custom integration (HACS) so you can
  set a custom `base_url`; the official OpenAI integration hardcodes OpenAI.

## Speech-to-text (Whisper)
The Jetson runs **whisper.cpp** (`whisper-server`) on `<jetson-ip>:8081` with an
HTTP `/inference` endpoint and automatic NL/EN detection. Bridge it into HA via a
Wyoming/whisper bridge, or run a Wyoming-Whisper satellite that posts to it.

## Text-to-speech (Piper) — OFF the Jetson
Run **Piper** on the mini-PC or as a Home Assistant **Wyoming add-on** (it's a
light CPU/ONNX task with no GPU benefit, so it must not consume the Jetson's 8GB).
HA auto-discovers the Wyoming-Piper service.

Settings → Voice assistants → create a pipeline:
`Whisper STT (Jetson) → Conversation agent (Jetson LLM) → Piper TTS (mini-PC/HA)`.

## Microphone & speakers
- **Sonos = output only:** use it as a `media_player`/announce target for TTS.
  Its built-in mic (and Google Nest) cannot feed HA Assist — no usable API, and
  Google-Assistant-on-Sonos was discontinued in 2024.
- **Voice input** needs a Wyoming satellite: **HA Voice PE** (recommended) or an
  ESP32 **Atom Echo**, which streams mic audio into the pipeline.

## Security
- Keep all of this on the LAN / VPN — do **not** expose `:8080`/`:8081` to the
  internet. No inbound router ports.
- HA voice control must not trigger high-impact agent actions (orders, payments)
  without the explicit approval gate handled by OpenClaw on the mini-PC.
