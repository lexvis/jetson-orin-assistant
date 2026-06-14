#!/usr/bin/env bash
# 01-system-config.sh — Jetson Orin Nano post-install system setup.
# Run on the device after first boot (booted from NVMe). Idempotent-ish.
set -euo pipefail

echo "==> Power mode: MAXN SUPER + max clocks"
sudo nvpmodel -m 0
sudo jetson_clocks

echo "==> Headless: disable desktop GUI to free RAM"
sudo systemctl set-default multi-user.target

echo "==> Base packages for agents that compile native deps"
sudo apt-get update
sudo apt-get install -y build-essential git cmake curl ca-certificates

echo "==> Node 24 (for OpenClaw)"
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt-get install -y nodejs

echo "==> Docker + NVIDIA runtime should be present via JetPack; verify:"
docker info 2>/dev/null | grep -i runtime || echo "  (check nvidia-container-runtime)"

echo "Done. Reboot recommended. Next: ./02-swap.sh"
