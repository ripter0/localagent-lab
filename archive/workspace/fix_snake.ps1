$content = Get-Content snake_game.html -Raw
$truncated = $content.Substring(0, 500)
Write-Host "Current content length: $($content.Length)"
Write-Host "Last 200 chars:" 
$content[-200] | ForEach-Object { Write-Host $_ }