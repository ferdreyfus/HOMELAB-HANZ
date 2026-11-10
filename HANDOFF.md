# HANZ — Handoff & runbook

**Host:** `HANZ` — Ryzen 5 5600X, 32 GB, RTX 3080 Ti 12 GB, Windows 11 Pro 10.0.26200.
**Tailnet:** `hanz` = **`100.91.105.67`**, unattended mode. NAS `nasty` = `100.83.67.9`, Mac = `100.85.120.21`.
**LAN:** `192.168.68.60/22`, Wi-Fi, DHCP (not reserved). Do not hardcode it.

---

## Current state — 2026-11-09

| | |
|---|---|
| Tailscale | ✅ 1.104.5, `--unattended`, **direct** path to `nasty` (21 ms via `192.168.68.20:41641`) |
| Ollama | ✅ 0.40.15, native Windows, listening `:11434` |
| Ollama firewall | ✅ allow `100.64.0.0/10`, block RFC1918 — **verified from `nasty`**: tailnet `200`, LAN `000` |
| HANZ → NAS SSH | ✅ `ssh nasty@100.83.67.9` works (Tailscale SSH, no key needed) |
| NAS → HANZ SSH | ❌ not set up |
| SVM / WSL2 | ❌ SVM disabled in BIOS — WSL2 Ubuntu cannot start |
| Ethernet / WoL | ⏸ deferred by decision — **the NAS cannot wake this box** |
| Bazzite | ⏸ not installed; target disk is the 860 EVO (Disk 1, `O:`, empty) |

## Run order (Windows)

```powershell
# elevated — firewall first, so the listener is never LAN-exposed
powershell -ExecutionPolicy Bypass -File windows\10-ollama.ps1
# normal user — env vars, restarts Ollama
powershell -ExecutionPolicy Bypass -File windows\ollama-env.ps1
```

Verify from the NAS (expect a version, then `000`):

```bash
curl -s http://100.91.105.67:11434/api/version
curl -s -m 5 -o /dev/null -w '%{http_code}\n' http://192.168.68.60:11434/api/version
```

## Benchmarks

`python bench/bench.py <model>` appends to `bench/results.jsonl`. Run the **same
model, same script** on Bazzite before choosing the primary AI OS. Close games
and Apollo streams first — VRAM in use skews the result.

---

## ⚠️ Known open items

1. **Enable SVM** in BIOS (*Tweaker → Advanced CPU Settings → SVM Mode*). Needed for WSL2/Docker.
2. **No Wake-on-LAN** until Ethernet is cabled. Until then, if HANZ sleeps, remote AI stops.
   Decide: leave it on (set sleep to *Never* on AC) or accept that it is only available while in use.
3. **NAS → HANZ SSH**: Windows OpenSSH server + the NAS's key (the NAS has no keypair yet — see HOMELAB-NAS HANDOFF).
4. **Router on the NAS**: `stacks/ai/` (LiteLLM + Open WebUI) belongs in HOMELAB-NAS. Point it at `hanz:11434`.
5. **Ollama has no auth.** The firewall is the only control. Never route `:11434` through cloudflared;
   expose AI publicly, if ever, only via LiteLLM/Open WebUI with keys.
