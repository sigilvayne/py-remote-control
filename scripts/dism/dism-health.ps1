[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$logFolder = 'C:\Script\logs'
$logFile = "$logFolder\dism.txt"
if (-not (Test-Path $logFolder)) { New-Item -ItemType Directory -Path $logFolder -Force | Out-Null }

"==== Перевірка цілісності системи $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ====" | Out-File -FilePath $logFile -Append -Encoding utf8

try {
    DISM /Online /Cleanup-Image /CheckHealth | Out-File -FilePath $logFile -Append -Encoding utf8
    DISM /Online /Cleanup-Image /ScanHealth | Out-File -FilePath $logFile -Append -Encoding utf8
    DISM /Online /Cleanup-Image /RestoreHealth | Out-File -FilePath $logFile -Append -Encoding utf8
} catch {
    "Помилка перевірки: $_" | Out-File -FilePath $logFile -Append -Encoding utf8
}

"" | Out-File -FilePath $logFile -Append -Encoding utf8
