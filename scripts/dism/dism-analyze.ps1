$output = dism /Online /Cleanup-Image /AnalyzeComponentStore 2>&1

$report = $output | Where-Object { $_ -match '^(Component Store (.*)|Date|Backups|Cache Size|Recommended|Suggested|.*reclaimable)' }

Write-Output ($report -join "`n")
