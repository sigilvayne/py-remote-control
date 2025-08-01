$output = dism /Online /Cleanup-Image /StartComponentCleanup /ResetBase /Quiet 2>&1

$success = if ($LASTEXITCODE -eq 0) { "Cleanup completed successfully." } else { "Cleanup encountered issues." }

$finalReport = "DISM CLEANUP REPORT:`nStatus: $success`nRaw Output:`n" + ($output -join "`n")
Write-Output $finalReport
