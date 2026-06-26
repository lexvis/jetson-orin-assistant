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
nvpmodel -q      # MAXN_SUPER
cat /proc/device-tree/model                 # ...Developer Kit Super
grep COMPATIBLE_SPEC /etc/nv_boot_control.conf   # must end in ...devkit-super-
```

> If your dev kit shipped with factory firmware too old for JetPack 7, run
> NVIDIA's "JetPack 6.x update path" once, then retry the JP7 installer.

## Fix: MAXN_SUPER missing / GPU stuck at 624 MHz (known JP7.2 ISO bug)

**Symptom.** Only 7W/15W power modes are offered, or `nvpmodel -q` reports
`MAXN_SUPER` yet the GPU never exceeds **624.75 MHz** and EMC stays at **2133 MHz**
(~68 GB/s). `/proc/device-tree/model` reads "Developer Kit" without "Super", and
`/etc/nv_boot_control.conf` `COMPATIBLE_SPEC` ends in `...jetson-orin-nano-devkit-`
(no `-super`).

**Cause.** The JetPack 7.2 *Jetson-ISO* installer provisions the **non-super device
tree**, so the BPMP firmware OPP tables omit the higher Super frequencies. nvpmodel
can only select *within* that table, so MAXN_SUPER is cosmetic. This is a confirmed
NVIDIA bug (forum topic 372627; NVIDIA staff: *"the ISO image cannot upgrade a
device from non-Super Mode to Super Mode"*).

**On-device fix (no x86 host, ~4 min + 1 reboot).** Back up first, then:
```bash
sudo cp /etc/nv_boot_control.conf /root/nv_boot_control.conf.bak
sudo -i
# 1. flag the board as the Super variant (rewrites both TNSPEC + COMPATIBLE_SPEC)
perl -i -0777 -pe 's/nano-devkit-\n/nano-devkit-super-\n/g' /etc/nv_boot_control.conf
# 2. reflash the QSPI bootloader/BPMP firmware from the installed BSP (super OPPs)
dpkg-reconfigure nvidia-l4t-bootloader
# 3. drop the wrong nvpmodel symlink; it regenerates to the _super conf on boot
rm /etc/nvpmodel.conf
reboot
```
After reboot:
```bash
sudo nvpmodel -m 2 --verbose --force        # 0/1/2 = 15W / 25W / MAXN_SUPER
```

**Verify the fix worked:**
```bash
grep COMPATIBLE_SPEC /etc/nv_boot_control.conf      # ...devkit-super-
cat /proc/device-tree/model                          # ...Developer Kit Super
cat /sys/devices/platform/bus@0/*.gpu/devfreq/*/available_frequencies | tr ' ' '\n' | tail -1   # 1020000000
cat /sys/kernel/debug/bpmp/debug/clk/emc/max_rate    # 3199000000
```
Expected gain: GPU 624.75 -> **1020 MHz**, EMC 2133 -> **3199 MHz** (~102 GB/s),
Qwen3-8B Q4 throughput ~7.3 -> **~11.6 tok/s**. MAXN_SUPER uses DVFS, so clocks
scale up only under load and idle back down (no need to pin `jetson_clocks`).

> Fallback if the in-place fix doesn't fully apply (e.g. EMC still 2133 MHz):
> reflash from an x86 Ubuntu host with
> `sudo ./l4t_initrd_flash.sh --erase-all jetson-orin-nano-devkit-super internal`.
