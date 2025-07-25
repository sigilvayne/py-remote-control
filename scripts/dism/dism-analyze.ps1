[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$logFolder = 'C:\Script\logs'
$logFile = "$logFolder\dism.txt"
if (-not (Test-Path $logFolder)) { New-Item -ItemType Directory -Path $logFolder -Force | Out-Null }

"==== Аналіз компонентного сховища $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ====" | Out-File -FilePath $logFile -Append -Encoding utf8

try {
    DISM /Online /Cleanup-Image /AnalyzeComponentStore | Out-File -FilePath $logFile -Append -Encoding utf8
} catch {
    "Помилка аналізу: $_" | Out-File -FilePath $logFile -Append -Encoding utf8
}

"" | Out-File -FilePath $logFile -Append -Encoding utf8
