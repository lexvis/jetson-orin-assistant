# Home Assistant integration (Assist + Voice)

Connect HA's **Assist** pipeline to this stack:

## Voice (Wyoming)
HA auto-discovers Wyoming services. Add integrations pointing at the Jetson:
- **Whisper (STT):** `wyoming-whisper` on `<jetson-ip>:10300`
- **Piper (TTS):** `wyoming-piper` on `<jetson-ip>:10200`

Settings → Voice assistants → create a pipeline:
`Whisper (STT) → Conversation agent (LLM) → Piper (TTS)`.

## Conversation agent (LLM)
Point HA at the OpenAI-compatible endpoint:
- **Local:** `http://<jetson-ip>:8080/v1` (llama-server).
- Use the **Extended OpenAI Conversation** custom integration (HACS) so you can
  set a custom `base_url`; the official OpenAI integration hardcodes OpenAI.

## Security
- Keep all of this on the LAN / WireGuard network — do **not** expose to the
  internet. No inbound router ports.
- HA voice control should not trigger high-impact agent actions (orders,
  payments) without the explicit approval gate handled by OpenClaw.
