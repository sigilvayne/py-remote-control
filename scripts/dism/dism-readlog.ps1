[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$logFile = 'C:\Script\logs\dism.txt'
if (Test-Path $logFile) {
    Get-Content -Path $logFile -Tail 100
} else {
    Write-Output "Лог-файл не знайдено: $logFile"
} 