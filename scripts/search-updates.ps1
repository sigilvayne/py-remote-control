$logFolder = 'C:\Script\logs'
$logFile   = "$logFolder\update.txt"

if (-not (Test-Path $logFolder)) {
    New-Item -ItemType Directory -Path $logFolder -Force | Out-Null
}

# Встановлюємо кодування Windows-1251
$encoding = [System.Text.Encoding]::GetEncoding(1251)
$writer = New-Object System.IO.StreamWriter($logFile, $true, $encoding)

function Write-Log {
    param([string]$text)
    $writer.WriteLine($text)
}

Write-Log "==== Перевірка оновлень $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===="

# Антивірус
Write-Log ''
Write-Log '[Антивірус]'
try {
    Update-MpSignature | Out-Null
    Start-Sleep -Seconds 5
    $status = Get-MpComputerStatus
    Write-Log "Версія бази: $($status.AntispywareSignatureVersion)"
} catch {
    Write-Log "Помилка оновлення антивіруса: $_"
}

# Windows Update
Write-Log ''
Write-Log '[Оновлення Windows]'
try {
    $updates = Get-WindowsUpdate -MicrosoftUpdate -IgnoreUserInput -AcceptAll -WhatIf
    if ($updates.Count -gt 0) {
        foreach ($u in $updates) {
            $title = $u.Title
            $severity = $u.MsrcSeverity
            $size = $u.Size
            Write-Log "$title | Severity: $severity | Size: $size байт"
        }
    } else {
        Write-Log 'Оновлень не знайдено.'
    }
} catch {
    Write-Log "Помилка перевірки оновлень: $_"
}

Write-Log ''
Write-Log ('-' * 60)
Write-Log ''

$writer.Close()
