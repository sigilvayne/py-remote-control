$taskName = "RDP_Guard"

try {
    Start-ScheduledTask -TaskName $taskName
    Write-Output "Task '$taskName' started successfully."
} catch {
    Write-Error "Failed to start task '$taskName'. Error: $_"
}
