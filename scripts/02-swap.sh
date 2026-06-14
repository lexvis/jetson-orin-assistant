#!/usr/bin/env bash
# 02-swap.sh — create swap on the NVMe as an OOM safety net for the 8GB Jetson.
set -euo pipefail

# After rootOnNVMe migration the NVMe is the root filesystem (/), so a plain
# /swapfile already lives on the SSD. There is no separate /mnt/nvme.
SWAPFILE=/swapfile
SIZE_GB="${1:-12}"   # default 12GB; pass an arg to override

if [ -f "$SWAPFILE" ]; then
  echo "Swapfile already exists at $SWAPFILE"; exit 0
fi

echo "==> Creating ${SIZE_GB}GB swap at $SWAPFILE"
sudo fallocate -l "${SIZE_GB}G" "$SWAPFILE" || \
  sudo dd if=/dev/zero of="$SWAPFILE" bs=1M count=$((SIZE_GB*1024))
sudo chmod 600 "$SWAPFILE"
sudo mkswap "$SWAPFILE"
sudo swapon "$SWAPFILE"

if ! grep -q "$SWAPFILE" /etc/fstab; then
  echo "$SWAPFILE none swap sw 0 0" | sudo tee -a /etc/fstab
fi

echo "==> Lower swappiness (use swap only under pressure)"
echo 'vm.swappiness=10' | sudo tee /etc/sysctl.d/99-swappiness.conf
sudo sysctl -p /etc/sysctl.d/99-swappiness.conf
free -h
