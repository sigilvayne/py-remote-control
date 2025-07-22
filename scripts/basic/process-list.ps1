# Показує процеси разом з користувачами, які їх запустили
$processes = Get-WmiObject Win32_Process
$processes | ForEach-Object {
    $owner = $_.GetOwner()
    [PSCustomObject]@{
        ProcessName = $_.Name
        PID         = $_.ProcessId
        User        = "$($owner.Domain)\$($owner.User)"
        Path        = $_.ExecutablePath
    }
} | Sort-Object User | Format-Table -AutoSize
