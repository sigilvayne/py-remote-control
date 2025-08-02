$cli = "C:\Program Files (x86)\RdpGuard\rdpguard-cli.exe"
$arguments = @("/license", "show")

$output = & "$cli" @arguments

if ($LASTEXITCODE -ne 0 -or !$output) {
    Write-Error "Failed to get license information."
    exit 1
}

Write-Output "`n--- RdpGuard License Information ---`n"
$output | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" } | Write-Output
