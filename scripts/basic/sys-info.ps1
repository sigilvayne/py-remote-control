$cpuCores = (Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfCores -Sum).Sum
$ramGB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 0)
$diskGB = [math]::Round((Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'").Size / 1GB, 0)
$resources = "$cpuCores/$ramGB/$diskGB"

$os = Get-CimInstance Win32_OperatingSystem
$osVersion = "$($os.Caption) $($os.Version) $($os.OSArchitecture)"

$serviceName = "Zabbix Agent"
$service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
$serviceStatus = if ($service) { $service.Status } else { "Not found" }

$uptime = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
$uptimeSpan = (Get-Date) - ([Management.ManagementDateTimeConverter]::ToDateTime($uptime))
$uptimeFormatted = "{0} days, {1} hours, {2} minutes" -f $uptimeSpan.Days, $uptimeSpan.Hours, $uptimeSpan.Minutes

$sessions = (quser.exe 2>$null) -replace '\s{2,}', ' ' | Select-Object -Skip 1
$activeUsersCount = if ($sessions) { ($sessions | Measure-Object).Count } else { 0 }

$processNames = @("1cv8s", "ezvit")
$userProcesses = @()

foreach ($sessionLine in $sessions) {
    $parts = $sessionLine.Split(' ')
    $username = $parts[0]

    $userProcs = Get-Process -IncludeUserName -ErrorAction SilentlyContinue | Where-Object {
        $_.UserName -like "*\$username" -and ($processNames -contains $_.ProcessName)
    }

    foreach ($proc in $processNames) {
        $hasProc = if ($userProcs.ProcessName -contains $proc) { "yes" } else { "no" }
        $userProcesses += "$hasProc : $username : $proc"
    }
}

Write-Output "Resources: $cpuCores cores, $ramGB GB RAM, $diskGB GB disk"
Write-Output "Resources (cores/ram/disk): $resources"
Write-Output "OS version: $osVersion"
Write-Output "Service $serviceName status: $serviceStatus"
Write-Output "Uptime: $uptimeFormatted"
Write-Output "Active users count: $activeUsersCount"
Write-Output "Processes 1cv8s, ezvit running per user:"
$userProcesses | Sort-Object | ForEach-Object { Write-Output $_ }
