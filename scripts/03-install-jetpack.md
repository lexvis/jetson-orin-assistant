# Install JetPack to the NVMe (USB-ISO, JetPack 7.2 / L4T r39.2)

Goal: install Jetson Linux **directly onto the NVMe SSD** using NVIDIA's "Jetson
ISO" installer on a throwaway USB stick. No SD card, no rootfs clone, no x86
Linux host. The USB stick is boot media (like a DVD) and is removed afterwards.

## On Windows: write the ISO to a USB stick
1. Download the **Jetson ISO** (r39.2) from NVIDIA's JetPack download page.
2. Verify the download is complete (size / `Get-FileHash <iso> -Algorithm SHA256`,
   compare with `JETSON_ISO_SHA256` in `versions.env`).
3. Write it to a **>=16GB USB stick** with **balenaEtcher**
   (*Flash from file* -> *Select target* = the USB stick -> *Flash*).

> The firmware (QSPI capsule) update is **baked into the ISO** - no internet is
> needed for it. Internet is only needed later (first-boot network, apt, models).

## On the Jetson: boot the USB and install
> Display is only on the **DisplayPort** connector (no HDMI; **USB-C carries no
> video**). The UEFI prompts cannot be driven over USB-C, so use a DisplayPort
> monitor + USB keyboard (or a USB-to-TTL serial cable) for this one-time setup.
> Afterwards the device runs fully headless via SSH.

1. Attach a DisplayPort monitor + USB keyboard, Ethernet, the NVMe, and the USB
   stick, then connect the included **19V** power supply.
2. Press **Esc** at the NVIDIA splash -> **Boot Manager** -> select the USB stick.
3. **Press `Y` within 30 seconds** to accept the QSPI firmware capsule update.
   This is the most-missed step; if it times out the install fails later. The
   update runs in **two passes** with reboots - this is expected.
4. At the GRUB menu choose **Install Jetson ISO r39.2**, select the **NVMe SSD**
   as the target (not the USB, not a microSD), and confirm. This **erases** the NVMe.
5. Reboot when prompted and **remove the USB stick** - the system now runs
   entirely from the NVMe.

## First boot (from NVMe)
Complete the Ubuntu setup: EULA, language, **network**, create your **user +
hostname**. Then set the power mode to **MAXN SUPER**.

`openssh-server` is enabled by default on L4T, so the device is reachable over the
network immediately after first-boot setup:
```bash
ssh <user>@<jetson-ip>      # find the IP in the top bar or your router
```

## Verify
```bash
lsblk            # root (/) should be on nvme0n1p1
nvpmodel -q      # MAXN SUPER
```

> If your dev kit shipped with factory firmware too old for JetPack 7, run
> NVIDIA's "JetPack 6.x update path" once, then retry the JP7 installer.
