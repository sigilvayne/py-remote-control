$logPath = "C:\Script\log"
$logFile = "$logPath\update.txt"

if (-not (Test-Path $logPath)) {
    New-Item -Path $logPath -ItemType Directory -Force | Out-Null
}

if (-not (Test-Path $logFile)) {
    New-Item -Path $logFile -ItemType File -Force | Out-Null
}

"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ==== Оновлення запущено ====" | Tee-Object -FilePath $logFile -Append

Install-Module PSWindowsUpdate -Force -Scope CurrentUser -ErrorAction SilentlyContinue | Tee-Object -FilePath $logFile -Append
Import-Module PSWindowsUpdate | Tee-Object -FilePath $logFile -Append

Get-WindowsUpdate -AcceptAll -Install -IgnoreReboot | Tee-Object -FilePath $logFile -Append

Update-MpSignature | Tee-Object -FilePath $logFile -Append

"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ==== Скрипт виконано успішно ====" | Tee-Object -FilePath $logFile -Append
