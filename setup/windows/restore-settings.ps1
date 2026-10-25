# Restore the Windows user settings this project needs (user level only, no admin, safe to run twice).
#   powershell -ExecutionPolicy Bypass -File setup\windows\restore-settings.ps1
# Then quit Ollama from the tray and start it again, and open a new terminal.

$vars = @{
    "OLLAMA_CONTEXT_LENGTH"  = "65536"  # default context for tools that don't set num_ctx (OpenCode)
    "OLLAMA_FLASH_ATTENTION" = "1"      # needed for the compressed cache
    "OLLAMA_KV_CACHE_TYPE"   = "q8_0"   # half-size context cache: 122k -> 188k context on 12 GB
}
foreach ($name in $vars.Keys) {
    [Environment]::SetEnvironmentVariable($name, $vars[$name], "User")
    Write-Host "set $name=$($vars[$name])"
}

# PATH: Python 3.14, its Scripts folder, and the user's WindowsApps folder (winget)
$want = @(
    "$env:LOCALAPPDATA\Programs\Python\Python314",
    "$env:LOCALAPPDATA\Programs\Python\Python314\Scripts",
    "$env:LOCALAPPDATA\Microsoft\WindowsApps"
)
$path = [Environment]::GetEnvironmentVariable("Path", "User")
$parts = $path -split ";" | Where-Object { $_ }
foreach ($dir in $want) {
    if ($parts -notcontains $dir) {
        $parts += $dir
        Write-Host "added to PATH: $dir"
    }
}
[Environment]::SetEnvironmentVariable("Path", ($parts -join ";"), "User")

# OpenCode config and rules
$oc = Join-Path $env:USERPROFILE ".config\opencode"
New-Item -ItemType Directory -Force $oc | Out-Null
Copy-Item (Join-Path $PSScriptRoot "..\opencode\opencode.jsonc"), (Join-Path $PSScriptRoot "..\opencode\AGENTS.md") $oc -Force
Write-Host "OpenCode config copied to $oc"

Write-Host "`nDone. Restart Ollama (tray icon -> Quit, then start it) and open a new terminal."
