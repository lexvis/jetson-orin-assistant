# llama.cpp (llama-server) on the Jetson — native CUDA build

OpenAI-compatible LLM inference server, built **natively** (no Docker) against
the host CUDA 13.2 and served as a systemd service on `:8080`. This is the
primary chat backend; the mini-PC orchestrator (OpenClaw) calls it over the LAN.

## Build (CUDA sm_87)
```
sudo apt install -y cuda-minimal-build-13-2 cuda-nvrtc-dev-13-2 \
  libcublas-dev-13-2 cmake g++ libcurl4-openssl-dev ccache git
export PATH=/usr/local/cuda-13.2/bin:$PATH
export CUDACXX=/usr/local/cuda-13.2/bin/nvcc

cd /opt && git clone --depth 1 https://github.com/ggml-org/llama.cpp.git
cd llama.cpp
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=87 \
  -DLLAMA_CURL=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build -j$(nproc) --target llama-server llama-cli
```
> `libcublas-dev-13-2` is required — without it CMake fails with
> `CUDA::cublas target not found`. The kernel/flash-attn compile takes ~25–35 min.

## Model files (on NVMe, not committed)
The NVMe **is** the root filesystem (`/`), so there is no separate `/mnt/nvme`.
Place GGUF weights under `/opt/models/` (`sudo mkdir -p /opt/models`).

- This build: **Qwen3-8B-Q4_K_M.gguf** (~4.8GB, strong NL/EN). Text-only.
- Download from a trusted GGUF source; verify it loads; pin the filename in
  `versions.env`.

## systemd service (`/etc/systemd/system/llama-server.service`)
```
[Service]
User=lex
Environment=PATH=/usr/local/cuda-13.2/bin:/usr/bin:/bin
Environment=LD_LIBRARY_PATH=/usr/local/cuda-13.2/lib64
ExecStart=/opt/llama.cpp/build/bin/llama-server \
  -m /opt/models/Qwen3-8B-Q4_K_M.gguf -ngl 99 -c 8192 -fa on \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  --host 0.0.0.0 --port 8080 --alias qwen3-8b
Restart=on-failure
```
```
sudo systemctl enable --now llama-server
```

## Memory budget (8GB unified)
| Component | ~RAM |
|---|---|
| OS (headless, minimised) | ~0.7 GB |
| Qwen3-8B Q4 + KV (c=8192, q8_0) | ~5.2 GB |
| Whisper large-v3-turbo Q5 (STT) | ~0.55 GB |
| **Both services loaded (measured)** | **6.9 / 7.3 GB** |

No room for a third large model — keep TTS/agent on the mini-PC, keep 16GB swap.

## Performance
Qwen3-8B Q4 generates ~7.5–9 tok/s on the Orin Nano Super (memory-bandwidth
bound). Normal and comfortably faster than reading speed.

## Health check
```
curl http://127.0.0.1:8080/v1/models
```
