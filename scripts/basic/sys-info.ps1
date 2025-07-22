# Повна інформація про систему, мережу та ресурси
$hostname = $env:COMPUTERNAME
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -ne $null}).IPAddress
$os = Get-CimInstance Win32_OperatingSystem
$cpu = Get-CimInstance Win32_Processor
$ram = "{0:N2} GB" -f (($os.TotalVisibleMemorySize) / 1MB)

Write-Host "=== Системна інформація ==="
Write-Host "Ім’я комп’ютера: $hostname"
Write-Host "Операційна система: $($os.Caption) $($os.OSArchitecture)"
Write-Host "Версія: $($os.Version)"
Write-Host "Час останнього запуску: $($os.LastBootUpTime)"
Write-Host "Процесор: $($cpu.Name)"
Write-Host "Оперативна пам’ять: $ram"

Write-Host "`n=== Мережа ==="
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -ne "127.0.0.1"} | Format-Table InterfaceAlias, IPAddress

Write-Host "`n=== Відкриті порти ==="
netstat -ano | Select-String LISTENING

Write-Host "`n=== Дисковий простір ==="
Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{Name='Size(GB)';Expression={"{0:N2}" -f ($_.Used+$_.Free/1GB)}}, @{Name='Free(GB)';Expression={"{0:N2}" -f ($_.Free/1GB)}}

Write-Host "`n=== Активні мережеві з'єднання ==="
Get-NetTCPConnection | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess | Format-Table -AutoSize
