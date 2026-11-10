#Requires -RunAsAdministrator
<#
  Ollama on HANZ: listen on all interfaces, but only the tailnet may connect.
  Idempotent. Run from an elevated PowerShell:
      powershell -ExecutionPolicy Bypass -File windows\10-ollama.ps1

  Windows Firewall evaluates BLOCK before ALLOW, so the RFC1918 block rule wins
  even if Windows later auto-creates an "allow ollama.exe" rule from a prompt.
  The tailnet (100.64.0.0/10) is not RFC1918, so it is unaffected.
#>
$ErrorActionPreference = 'Stop'

$allow = 'HOMELAB Ollama - allow tailnet'
$block = 'HOMELAB Ollama - block LAN'

Get-NetFirewallRule -DisplayName $allow, $block -ErrorAction SilentlyContinue | Remove-NetFirewallRule

New-NetFirewallRule -DisplayName $allow -Direction Inbound -Action Allow `
  -Protocol TCP -LocalPort 11434 -RemoteAddress 100.64.0.0/10 -Profile Any | Out-Null

New-NetFirewallRule -DisplayName $block -Direction Inbound -Action Block `
  -Protocol TCP -LocalPort 11434 -RemoteAddress 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 -Profile Any | Out-Null

Get-NetFirewallRule -DisplayName $allow, $block |
  ForEach-Object { '{0,-35} {1,-6} {2}' -f $_.DisplayName, $_.Action, $_.Enabled }
