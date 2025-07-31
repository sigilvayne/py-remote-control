# Active RDP Users Script
# This script shows currently active RDP users

Write-Output "Пошук активних користувачів RDP..."

try {
    # Get active RDP sessions
    $sessions = quser 2>$null
    
    if ($sessions) {
        Write-Output "Активні сеанси RDP:"
        Write-Output "----------------------------------------"
        Write-Output $sessions
        Write-Output "----------------------------------------"
    } else {
        Write-Output "Активних сеансів RDP не знайдено."
    }

    # Alternative method using Get-WmiObject
    Write-Output "Детальна інформація про активні сеанси:"
    Write-Output "----------------------------------------"
    
    $activeSessions = Get-WmiObject -Class Win32_LogonSession | Where-Object { $_.LogonType -eq 10 }
    
    if ($activeSessions) {
        foreach ($session in $activeSessions) {
            $user = Get-WmiObject -Class Win32_UserAccount | Where-Object { $_.SID -eq $session.LogonId }
            if ($user) {
                Write-Output "Користувач: $($user.Name)"
                Write-Output "Домен: $($user.Domain)"
                Write-Output "Час входу: $($session.StartTime)"
                Write-Output "----------------------------------------"
            }
        }
    } else {
        Write-Output "Активних користувачів не знайдено."
    }

} catch {
    Write-Output "Помилка при отриманні інформації про користувачів: $($_.Exception.Message)"
} 