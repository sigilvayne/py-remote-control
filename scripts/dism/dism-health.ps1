$output = dism /Online /Cleanup-Image /ScanHealth 2>&1

$report = ($output | Where-Object { $_ -match 'No component store corruption|The component store is repairable|Repairable' })

if (-not $report) {
    $report = "No conclusive result found in DISM output."
}

Write-Output ($report -join "`n")
