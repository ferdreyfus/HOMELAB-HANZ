# Homelab — HANZ (GPU workstation)

Third host in the homelab, next to [`HOMELAB-NAS`](https://github.com/ferdreyfus/HOMELAB-NAS)
(`nasty`, the always-on Debian box) and [`HOMELAB-BOTS`](https://github.com/ferdreyfus/HOMELAB-BOTS)
(the retired macOS homelab; the MacBook Pro is now the dev host).

**Host:** `HANZ` — custom desktop, Windows 11 Pro (Bazzite dual-boot planned).
**Role:** the homelab's **GPU worker** — local AI first, gaming second.
**Tailnet:** `hanz` = **`100.91.105.67`**. Direct path to `nasty` verified 2026-11-09 (21 ms, no DERP relay).
**LAN:** `192.168.68.60/22` on **Wi-Fi**, DHCP — ⚠️ inside the Deco pool, so it can drift. Use the tailnet name.

---

## Hardware as surveyed 2026-11-09

| | |
|---|---|
| Board | Gigabyte X570 AORUS PRO WIFI, BIOS F30, UEFI boot |
| CPU | AMD Ryzen 5 5600X, 6c/12t Zen3 |
| RAM | 32 GB — 2× 16 GB Kingston HyperX DDR4-3200 (`HX432C16FB3/16`) |
| GPU | **NVIDIA RTX 3080 Ti, 12 GB**, compute capability 8.6, driver 591.86 |
| Disk 3 | 2 TB HS-SSD-FUTURE Lite NVMe — `C:` Windows (boot) |
| Disk 0 | 1 TB AGI SATA SSD — `G:` |
| Disk 1 | 500 GB Samsung 860 EVO M.2 SATA — `O:`, **empty** → reserved for Bazzite |
| Disk 2 | 250 GB Samsung 850 EVO SATA — `F:` |
| NICs | Intel AX200 Wi-Fi 6 (in use) · Intel I211 1 GbE (**unplugged**) |
| Sleep | S3 only |

### ⚠️ Found by the survey
- **SVM (AMD-V) is disabled in the BIOS** — `VirtualizationFirmwareEnabled = False`, no hypervisor.
  WSL2 (`Ubuntu` is installed) and Docker Desktop cannot run until it is enabled:
  BIOS → *Tweaker → Advanced CPU Settings → SVM Mode → Enabled*.
- **Wi-Fi only.** Wake-on-LAN needs the I211 cabled. Deferred by decision (below).

---

## Decisions — 2026-11-09

1. **AI over gaming.** The primary OS is whichever runs Ollama better *on this box*.
   Windows first because it is installed; Bazzite gets the same benchmark once it is
   (`bench/bench.py`). Numbers in `bench/results.jsonl` decide.
2. **No Ethernet for now.** Consequence: **no Wake-on-LAN**. Remote AI only works
   while HANZ is powered on and awake — the NAS cannot wake it.
3. **Separate repo** (this one), matching the per-host layout of the other two.

---

## Service inventory

| Service | Port | Reachable from | Notes |
|---|---|---|---|
| Ollama | 11434 | **tailnet only** (`100.64.0.0/10`) | Firewall: allow tailnet, block RFC1918. No auth — never tunnel it publicly |
| Apollo | 47984-48010 | LAN | Game streaming (Sunshine fork). Virtual display driver installed |
| Tailscale | 41641/udp | — | `hanz`, unattended mode |

---

## Layout

```
windows/        PowerShell setup + toggles, run on Windows
bench/          cross-platform Ollama benchmark (Windows vs Bazzite)
docs/plan.md    the integration plan: how the hosts share compute
HANDOFF.md      current state, run order, open items
```
