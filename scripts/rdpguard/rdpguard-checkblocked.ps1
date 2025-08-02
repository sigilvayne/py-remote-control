$cli = "C:\Program Files (x86)\RdpGuard\rdpguard-cli.exe"
$outFile = "$PSScriptRoot\blocked_ips.json"

$arguments = @(
    "/ip",
    "export",
    "json",
    "`"$outFile`""
)

& "$cli" @arguments

if (Test-Path $outFile) {
    $json = Get-Content $outFile -Raw | ConvertFrom-Json

    if ($json.BlockedIPList) {
        $ips = $json.BlockedIPList | Select-Object -ExpandProperty IP

        Write-Output "Blocked IPs: $($ips.Count)"
        Write-Output ""
        $ips | ForEach-Object { Write-Output $_ }
    } else {
        Write-Output "No blocked IPs found."
    }
} else {
    Write-Error "File not created. Check if RdpGuard is installed and CLI is available."
}
