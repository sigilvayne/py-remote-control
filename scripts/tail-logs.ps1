# tail-logs.ps1

$logFile = 'C:\Script\logs\update.logs'

if (-not (Test-Path $logFile)) {
    Write-Host "Файл логу не знайдено: $logFile" -ForegroundColor Red
    exit 1
}

$encoding = [System.Text.Encoding]::GetEncoding(1251)
$lines = [System.IO.File]::ReadAllLines($logFile, $encoding)

$tail = if ($lines.Count -gt 20) { $lines[-20..-1] } else { $lines }
$tail | ForEach-Object { Write-Output $_ }
