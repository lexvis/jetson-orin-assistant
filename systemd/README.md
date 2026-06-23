# systemd units (Jetson inference node)

Service definitions for the native GPU inference services. Install on the Jetson:

```
sudo cp llama-server.service whisper-server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now llama-server whisper-server
systemctl is-active llama-server whisper-server   # both 'active'
```

| Unit | Engine | Model | Port |
|---|---|---|---|
| `llama-server.service` | llama.cpp (native, CUDA sm_87) | Qwen3-8B Q4_K_M | 8080 |
| `whisper-server.service` | whisper.cpp (native, CUDA sm_87) | large-v3-turbo Q5_0 | 8081 |

Both set `LD_LIBRARY_PATH=/usr/local/cuda-13.2/lib64` so the CUDA runtime
resolves. Adjust `User=` and the model paths if your layout differs.

To free a stuck port on restart use `sudo fuser -k 8080/tcp` — do **not** use
`pkill -f llama-server`, as the pattern also matches your own SSH command line.
