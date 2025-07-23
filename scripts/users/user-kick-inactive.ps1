# Завершити всі відключені RDP сесії (disconnected)

# Get all sessions
$sessions = quser | Select-String -Pattern 'Disc' | ForEach-Object {
    $parts = $_ -split '\s+'
    # Username is usually at index 1, session ID at index 2 or 3 depending on output
    $id = $parts | Where-Object { $_ -match '^\d+$' } | Select-Object -First 1
    $id
} | Where-Object { $_ }

foreach ($sessionId in $sessions) {
    try {
        logoff $sessionId /V
        Write-Output "Відключено сесію ID: $sessionId"
    } catch {
        Write-Output "Не вдалося завершити сесію ID: $sessionId. $_"
    }
} 