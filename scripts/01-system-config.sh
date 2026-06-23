#!/usr/bin/env bash
# 01-system-config.sh — Jetson Orin Nano post-install setup (INFERENCE NODE).
# Run on the device after first boot (booted from NVMe). Idempotent-ish.
# Scope: lean, headless, GPU inference only. No Docker, no Node/OpenClaw here.
set -euo pipefail

echo "==> Power mode: MAXN SUPER (mode 2), persistent, DVFS left ON"
sudo nvpmodel -m 2 || true
# NOTE: do NOT run 'jetson_clocks' as a persistent service — it pins max clocks
# and disables DVFS (wastes energy 24/7). nvpmodel sets the persistent ceiling.
# Make MAXN_SUPER the board default by editing the board conf itself (the /etc
# symlink is reset on boot): set 'DEFAULT 2' in
#   /etc/nvpmodel/nvpmodel_p3767_0003.conf   (back up the original as .orig).

echo "==> Headless: disable desktop GUI and remove it to free RAM"
sudo systemctl set-default multi-user.target
sudo apt-get purge -y 'ubuntu-desktop*' 'gnome-shell*' gdm3 'yaru-theme-*' || true
sudo apt-get autoremove --purge -y && sudo apt-get clean

echo "==> Minimal CUDA 13.2 build toolchain (native llama.cpp / whisper.cpp)"
sudo apt-get update
sudo apt-get install -y \
  cuda-minimal-build-13-2 cuda-nvrtc-dev-13-2 libcublas-dev-13-2 \
  cmake g++ libcurl4-openssl-dev ccache git build-essential
echo 'export PATH=/usr/local/cuda-13.2/bin:$PATH' | \
  sudo tee /etc/profile.d/cuda.sh >/dev/null
/usr/local/cuda-13.2/bin/nvcc --version | grep release || true

echo "==> Disable non-essential services (headless inference node)"
for svc in bluetooth ModemManager avahi-daemon cups cups-browsed \
           kerneloops apport gnome-remote-desktop switcheroo-control \
           power-profiles-daemon accounts-daemon isc-dhcp-server dnsmasq \
           openvpn anacron fwupd nvargus-daemon udisks2; do
  sudo systemctl disable --now "$svc" 2>/dev/null || true
done
sudo systemctl mask snapd 2>/dev/null || true

echo "Done. Next: ./02-swap.sh, then build llama.cpp + whisper.cpp (see PDF guide)."
