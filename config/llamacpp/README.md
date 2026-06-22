# llama.cpp (llama-server) on Jetson

OpenAI-compatible inference server for the **local** model (privacy/offline
fallback; cloud Opus via Copilot handles heavy work — see `config/openclaw`).

## Model files (on NVMe, not committed)
After the JetPack install the NVMe **is** the root filesystem (`/`), so there
is no separate `/mnt/nvme`. Place GGUF weights under `/opt/models/` (create it with
`sudo mkdir -p /opt/models`). For a multimodal (vision) model
you need both the model GGUF **and** its matching `--mmproj` projector:

- Balance pick: **Gemma 3 4B** Q4_K_M (+ mmproj) or **Qwen2.5-VL 3B** Q4 (+ mmproj).
- Download from a trusted GGUF source; verify checksums; pin the file name in
  `compose/docker-compose.yml` and `versions.env`.

## Server args (see docker-compose.yml)
```
llama-server \
  -m /models/<model>.gguf \
  --mmproj /models/<model>-mmproj.gguf \
  --host 0.0.0.0 --port 8080 \
  -ngl 99            # offload all layers to GPU
  --ctx-size 4096    # keep modest on 8GB
```

## Memory budget (8GB unified — keep it tight)
| Component | ~RAM |
|---|---|
| OS (headless) | 1.5 GB |
| Local model (3–4B Q4) | 3–4 GB |
| Whisper (base) | 0.5–1 GB |
| Piper | <0.2 GB |
| Open WebUI | 0.3 GB |
| OpenClaw (Node) | 0.3–0.5 GB |
| Chromium (on-demand) | 0.5–1.5 GB |

Run Chromium on-demand only; keep 8–16GB swap on NVMe; prefer the **cloud**
(Copilot) model for heavy multimodal/agent reasoning to relieve the 8GB.

## Health check
```
curl http://127.0.0.1:8080/v1/models
```
