$output = dism /Online /Cleanup-Image /StartComponentCleanup /ResetBase /Quiet 2>&1
Write-Output ($output -join "`n")
