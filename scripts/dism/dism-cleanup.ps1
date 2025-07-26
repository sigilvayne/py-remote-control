[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$logFolder = 'C:\Script\logs'
$logFile = "$logFolder\dism.txt"
if (-not (Test-Path $logFolder)) { New-Item -ItemType Directory -Path $logFolder -Force | Out-Null }

"==== Очистка компонентного сховища $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ====" | Out-File -FilePath $logFile -Append -Encoding utf8

try {
    DISM /Online /Cleanup-Image /StartComponentCleanup | Out-File -FilePath $logFile -Append -Encoding utf8
} catch {
    "Помилка очистки: $_" | Out-File -FilePath $logFile -Append -Encoding utf8
}

"" | Out-File -FilePath $logFile -Append -Encoding utf8
