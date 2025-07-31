# Failed RDP Login Attempts Script
# This script shows failed RDP login attempts

Write-Output "Пошук невдалих спроб входу по RDP..."

try {
    # Get failed login attempts from Security Event Log
    $failedLogins = Get-WinEvent -FilterHashtable @{
        LogName = 'Security'
        ID = 4625  # Failed logon
    } -MaxEvents 50 -ErrorAction SilentlyContinue
    
    Write-Output "Невдалі спроби входу:"
    Write-Output "----------------------------------------"
    
    if ($failedLogins) {
        foreach ($event in $failedLogins) {
            $time = $event.TimeCreated
            $user = $event.Properties[5].Value
            $ip = $event.Properties[19].Value
            $reason = $event.Properties[8].Value
            
            Write-Output "Час: $time"
            Write-Output "Користувач: $user"
            Write-Output "IP адреса: $ip"
            Write-Output "Причина: $reason"
            Write-Output "----------------------------------------"
        }
    } else {
        Write-Output "Невдалих спроб входу не знайдено."
    }

    # Get RDP-specific failed connections
    Write-Output "Невдалі RDP підключення:"
    Write-Output "----------------------------------------"
    
    $rdpFailEvents = Get-WinEvent -FilterHashtable @{
        LogName = 'Microsoft-Windows-TerminalServices-RemoteConnectionManager/Operational'
        ID = 1149, 4625
    } -MaxEvents 20 -ErrorAction SilentlyContinue
    
    if ($rdpFailEvents) {
        foreach ($event in $rdpFailEvents) {
            $time = $event.TimeCreated
            $message = $event.Message
            
            Write-Output "Час: $time"
            Write-Output "Повідомлення: $message"
            Write-Output "----------------------------------------"
        }
    } else {
        Write-Output "Невдалих RDP підключень не знайдено."
    }

    # Summary statistics
    Write-Output "Статистика невдалих входів:"
    Write-Output "----------------------------------------"
    
    $recentFailures = Get-WinEvent -FilterHashtable @{
        LogName = 'Security'
        ID = 4625
    } -MaxEvents 1000 -ErrorAction SilentlyContinue
    
    if ($recentFailures) {
        $failureCount = $recentFailures.Count
        $last24h = ($recentFailures | Where-Object { $_.TimeCreated -gt (Get-Date).AddDays(-1) }).Count
        $lastHour = ($recentFailures | Where-Object { $_.TimeCreated -gt (Get-Date).AddHours(-1) }).Count
        
        Write-Output "Всього невдалих спроб: $failureCount"
        Write-Output "За останні 24 години: $last24h"
        Write-Output "За останню годину: $lastHour"
    } else {
        Write-Output "Статистика недоступна."
    }

} catch {
    Write-Output "Помилка при отриманні інформації про невдалі входи: $($_.Exception.Message)"
} 