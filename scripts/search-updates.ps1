Import-Module PSWindowsUpdate -ErrorAction SilentlyContinue

if (-not (Get-Module -ListAvailable -Name PSWindowsUpdate)) {
    Write-Host "Модуль PSWindowsUpdate не знайдено. Встановлення..."
    Install-Module -Name PSWindowsUpdate -Force -Confirm:$false
    Import-Module PSWindowsUpdate
}

Write-Host "`n=== Перевірка оновлень антивіруса (Захисник Windows) ==="
try {
    Update-MpSignature -AsJob | Out-Null
    Start-Sleep -Seconds 5
    $status = Get-MpComputerStatus
    Write-Host "Версія антивірусної бази даних: $($status.AntispywareSignatureVersion)"
} catch {
    Write-Warning "Не вдалося перевірити оновлення антивіруса: $_"
}

Write-Host "`n=== Перевірка оновлень Windows ==="
try {
    $updates = Get-WindowsUpdate -MicrosoftUpdate -IgnoreUserInput -AcceptAll -WhatIf
    if ($updates) {
        $updates | Format-Table -Property Title, KB, Size, MsrcSeverity -AutoSize
    } else {
        Write-Host "Оновлень не знайдено."
    }
} catch {
    Write-Warning "Не вдалося отримати список оновлень: $_"
}
