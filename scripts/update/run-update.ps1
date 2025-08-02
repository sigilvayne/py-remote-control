Import-Module PSWindowsUpdate

$updates = Get-WindowsUpdate -MicrosoftUpdate -IgnoreUserInput -AcceptAll -Download -Install -AutoReboot:$false -ErrorAction SilentlyContinue

$installed = $updates | Where-Object { $_.IsInstalled }

$pending = $updates | Where-Object { -not $_.IsInstalled }

$finalReport = @"
WINDOWS UPDATE - INSTALLATION SUMMARY:
Updates Installed: $($installed.Count)
Pending/Failed: $($pending.Count)

Installed Updates:
$($installed.Title -join "`n")

Pending/Failed Updates:
$($pending.Title -join "`n")

Перезавантажте систему для завершення оновлення.
"@

Write-Output $finalReport
