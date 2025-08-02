$cli = "C:\Program Files (x86)\RdpGuard\rdpguard-cli.exe"

if (-not (Test-Path $cli)) {
    Write-Error "RDP guard not found: $cli"
    exit 1
}

$arguments = @("/ip", "unblock", "*")

& "$cli" @arguments

Write-Output "`nIPs unblocked!"
