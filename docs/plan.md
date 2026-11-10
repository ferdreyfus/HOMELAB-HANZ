# Integration plan — sharing compute across the homelab

## Roles

| Host | Role | Why |
|---|---|---|
| `nasty` (Debian NAS) | **Control plane, always on** — AI front door, router, job dispatch, monitoring, backups | Only box that is always up; already runs Docker, Tailscale, Beszel, the Telegram bot |
| `hanz` (this box) | **GPU worker, on demand** — local AI, batch GPU jobs, gaming | The only real GPU (RTX 3080 Ti, 12 GB) |
| `fernandos-macbook-pro` (M1 Pro) | **Dev host + client**, small-model fallback | Where code is written; 7–8B models run fine |
| `iphone183` | Client | Telegram bot, Open WebUI |

All traffic between hosts goes over **Tailscale**. Nothing is addressed by LAN IP.

## How "request compute" works

```
Mac / iPhone / bot / scripts
          │  http://nasty:4000   (OpenAI-compatible, one API key)
          ▼
   LiteLLM on nasty ──► hanz:11434           Ollama on the 3080 Ti     (first choice)
                    ──► hanz-bazzite:11434   same box, booted Linux
                    ──► mac:11434            Ollama on M1 Pro          (fallback)
```

Clients never need to know which box is up. Without Ethernet there is no
Wake-on-LAN, so "HANZ is off" simply means LiteLLM falls through to the Mac.

## How "push work" works

- **Interactive AI** → through the router above.
- **Batch jobs** (Whisper transcription, embeddings, OCR, encodes) → start with
  `ssh hanz '<cmd>'` over Tailscale from a NAS script. Add a real queue
  (Redis + a worker on HANZ) only when jobs start waiting on each other.
  No Kubernetes/Ray — one intermittent GPU box does not justify a scheduler.

## Phases

### 0 — Foundation
- [x] Tailscale on Windows, `hanz`, unattended (2026-11-09)
- [ ] BIOS: SVM Mode on (WSL2/Docker)
- [ ] Beszel agent → GPU temp/VRAM on the existing dashboard
- [ ] SSH: NAS and Mac → hanz (Windows OpenSSH server, key auth)
- [ ] *Deferred:* Ethernet, Deco reservation, Wake-on-LAN (BIOS WoL on, ErP off, Fast Startup off)

### 1 — Local AI on Windows
- [x] Ollama installed (0.40.15)
- [ ] `windows/10-ollama.ps1` — tailnet-only listener + firewall
- [ ] First model + baseline benchmark (`bench/bench.py`)
- [ ] NAS: `stacks/ai/` in HOMELAB-NAS — LiteLLM + Open WebUI
- [ ] Bot: `/ask`, `/gpu`

### 2 — Bazzite dual-boot
- [ ] `bazzite-nvidia` on the 860 EVO (Disk 1, `O:`), its own ESP — Windows' bootloader untouched
- [ ] Tailscale as `hanz-bazzite`, Ollama under Podman/quadlet
- [ ] Same benchmark → decide the primary AI OS → set it as default boot entry
- [ ] Separate Steam libraries per OS (no shared NTFS library)

### 3 — Gaming and AI share one GPU
- [ ] `windows/gaming-mode.ps1` — stop Ollama to free VRAM, restore after
- [ ] Router drains to the Mac while gaming mode is on
- [ ] Optional: trigger from Apollo session start/stop

### 4 — Later
- Immich ML / Jellyfin subtitles / Whisper offloaded to HANZ
- restic backup of HANZ `Documents` + saves to the NAS
- Tailscale ACL tags: `tag:server` (nasty), `tag:gpu` (hanz), `tag:dev` (Mac);
  only `server` and `dev` may reach `gpu:11434`
