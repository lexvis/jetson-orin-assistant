# NVMe migration (SD as throwaway bootstrap media)

Goal: use the microSD only to bootstrap, then run fully from the NVMe and
remove the SD. No x86 Linux host required.

## Steps
1. **Flash SD on Windows** with balenaEtcher: official JetPack 6.2 SD image.
2. **Boot once from SD**, finish Ubuntu first-boot setup.
3. **Firmware / Super mode** (on the Jetson itself):
   ```bash
   sudo apt update && sudo apt full-upgrade -y   # updates nvidia-l4t-bootloader (QSPI)
   sudo reboot
   ```
   (Dev kits shipped with JetPack 5.x need this before NVMe boot of JP6 works.)
4. **Clone rootfs SD → NVMe** with the JetsonHacks scripts (run on the Jetson):
   ```bash
   git clone https://github.com/jetsonhacks/rootOnNVMe.git
   cd rootOnNVMe
   ./copy-rootfs-ssd.sh
   ./setup-service.sh
   ```
5. Set NVMe first in the **UEFI boot order** if needed (boot menu / `efibootmgr`).
6. **Shut down, remove SD, boot** → system now runs entirely from the NVMe.

## Verify
```bash
lsblk            # root (/) should be on nvme0n1p1
nvpmodel -q      # MAXN SUPER
```

> The only "pure NVMe flash without clone" path is NVIDIA SDK Manager, which
> requires an x86 Linux host — intentionally avoided here.
