# Last Login Information Script
# This script shows last login information for each user

Write-Output "Отримання інформації про останні входи користувачів..."

try {
    # Get all local users
    $users = Get-LocalUser | Where-Object { $_.Enabled -eq $true }
    
    Write-Output "Останні входи користувачів:"
    Write-Output "----------------------------------------"
    
    foreach ($user in $users) {
        Write-Output "Користувач: $($user.Name)"
        Write-Output "Останній вхід: $($user.LastLogon)"
        Write-Output "Створено: $($user.CreationDate)"
        Write-Output "Активний: $($user.Enabled)"
        Write-Output "----------------------------------------"
    }

    # Get RDP connection history from Event Logs
    Write-Output "Історія підключень RDP:"
    Write-Output "----------------------------------------"
    
    $rdpEvents = Get-WinEvent -FilterHashtable @{
        LogName = 'Microsoft-Windows-TerminalServices-RemoteConnectionManager/Operational'
        ID = 1149
    } -MaxEvents 20 -ErrorAction SilentlyContinue
    
    if ($rdpEvents) {
        foreach ($event in $rdpEvents) {
            $time = $event.TimeCreated
            $user = $event.Properties[0].Value
            $ip = $event.Properties[1].Value
            
            Write-Output "Час: $time"
            Write-Output "Користувач: $user"
            Write-Output "IP адреса: $ip"
            Write-Output "----------------------------------------"
        }
    } else {
        Write-Output "Історія RDP підключень не знайдена."
    }

} catch {
    Write-Output "Помилка при отриманні інформації про входи: $($_.Exception.Message)"
} 