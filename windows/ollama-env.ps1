<#
  Ollama environment for HANZ (per-user; no admin needed). Restarts Ollama so it applies.

  OLLAMA_HOST            listen on all interfaces; 10-ollama.ps1 restricts who may connect
  OLLAMA_KEEP_ALIVE      unload a model from VRAM after 10 min idle (games need that VRAM back)
  OLLAMA_FLASH_ATTENTION faster attention, less VRAM on Ampere
  OLLAMA_KV_CACHE_TYPE   q8_0 halves the KV-cache VRAM vs f16 — longer context in 12 GB
#>
$vars = [ordered]@{
  OLLAMA_HOST            = '0.0.0.0:11434'
  OLLAMA_KEEP_ALIVE      = '10m'
  OLLAMA_FLASH_ATTENTION = '1'
  OLLAMA_KV_CACHE_TYPE   = 'q8_0'
}
foreach ($k in $vars.Keys) {
  [Environment]::SetEnvironmentVariable($k, $vars[$k], 'User')
  Set-Item "env:$k" $vars[$k]
  '{0} = {1}' -f $k, $vars[$k]
}

Get-Process 'ollama app', 'ollama' -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
Start-Process "$env:LOCALAPPDATA\Programs\Ollama\ollama app.exe"
