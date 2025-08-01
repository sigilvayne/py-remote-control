Import-Module PSWindowsUpdate

$updates = Get-WindowsUpdate -MicrosoftUpdate -IgnoreUserInput -AcceptAll -ErrorAction SilentlyContinue

$securityUpdates = $updates | Where-Object { $_.Title -match "Security" }
$regularUpdates = $updates | Where-Object { $_.Title -notmatch "Security" }

$finalReport = @"
WINDOWS UPDATE - AVAILABLE:
Total Updates: $($updates.Count)
Security Updates: $($securityUpdates.Count)
Regular Updates: $($regularUpdates.Count)

List:
$($updates.Title -join "`n")
"@

Write-Output $finalReport
