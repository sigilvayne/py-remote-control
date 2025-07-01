$User = "agent-gui"
$PwdLength = 20
$Pwd = -join ((33..126) | Get-Random -Count $PwdLength | ForEach-Object {[char]$_})
$SecurePwd = ConvertTo-SecureString $Pwd -AsPlainText -Force
$agent = "C:\Script\agent\agent.py"
$py = "C:\Script\agent\Python\python.exe"
$run = "`"$py`" `"$agent`""
$adminGrp = (Get-LocalGroup | Where SID -eq 'S-1-5-32-544').Name

if (-not (Get-LocalUser $User -EA SilentlyContinue)) {
    New-LocalUser $User -Password $SecurePwd -FullName "Agent GUI" -Description "Created by create-user.ps1"
    Add-LocalGroupMember $adminGrp $User
    $w = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
    New-ItemProperty $w -Name AutoAdminLogon -Value 1 -Force
    New-ItemProperty $w -Name DefaultUsername -Value $User -Force
    New-ItemProperty $w -Name DefaultPassword -Value $Pwd -Force
    exit
}

$SID = (Get-LocalUser $User).SID.Value
$hive = "C:\Users\$User\NTUSER.DAT"
$key = "HKEY_USERS\$SID"

reg load $key $hive

$runKey = "Registry::$key\Software\Microsoft\Windows\CurrentVersion\Run"
if (-not (Test-Path $runKey)) { New-Item $runKey -Force | Out-Null }
New-ItemProperty $runKey -Name Agent -Value $run -Force

foreach ($sub in 'Run','RunOnce') {
    $rk = "Registry::$key\Software\Microsoft\Windows\CurrentVersion\$sub"
    if (Test-Path $rk) {
        Get-ItemProperty $rk |
        Select-Object -Expand PSObject.Properties |
        Where-Object { $_.Name -notin 'PSPath','PSParentPath','PSChildName','PSDrive','PSProvider' } |
        ForEach-Object { if ($_.Name -ne 'Agent') { Remove-ItemProperty $rk -Name $_.Name -EA SilentlyContinue } }
    }
}

$wl = "Registry::$key\Software\Microsoft\Windows NT\CurrentVersion\Winlogon"
if (-not (Test-Path $wl)) { New-Item $wl -Force | Out-Null }
Set-ItemProperty $wl -Name Shell -Value $run -Force

reg unload $key
