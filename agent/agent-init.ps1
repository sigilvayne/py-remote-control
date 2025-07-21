# --- Налаштування ---
$User = "agent-gui"
$PwdLength = 20
$AgentPath = "C:\Script\agent\agent.exe"
$RunCommand = "`"$AgentPath`""
$LogFile = "C:\Script\create-user.log"

# --- Генерація пароля ---
$Pwd = -join ((33..126) | Get-Random -Count $PwdLength | ForEach-Object { [char]$_ })
$SecurePwd = ConvertTo-SecureString $Pwd -AsPlainText -Force

# --- Перевірка наявності файлу агенту ---
if (-not (Test-Path $AgentPath)) {
    Write-Warning "[$(Get-Date)] Agent not found at $AgentPath" | Out-File -Append $LogFile
    exit 1
}

# --- Отримання групи адміністраторів ---
$adminGrp = (Get-LocalGroup | Where SID -eq 'S-1-5-32-544').Name

# --- Створення користувача, якщо не існує ---
if (-not (Get-LocalUser $User -EA SilentlyContinue)) {
    try {
        New-LocalUser $User -Password $SecurePwd -FullName "Agent GUI" -Description "Created by create-user.ps1"
        Add-LocalGroupMember $adminGrp $User
        Write-Output "[$(Get-Date)] User $User created and added to $adminGrp." | Out-File -Append $LogFile

        # --- Налаштування автологіну ---
        $w = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
        Set-ItemProperty $w -Name AutoAdminLogon -Value 1 -Force
        Set-ItemProperty $w -Name DefaultUsername -Value $User -Force
        Set-ItemProperty $w -Name DefaultPassword -Value $Pwd -Force
    } catch {
        Write-Warning "[$(Get-Date)] Failed to create user or set autologon: $_" | Out-File -Append $LogFile
        exit 1
    }
    exit
}

# --- Завантаження профілю користувача ---
$SID = (Get-LocalUser $User).SID.Value
$Hive = "C:\Users\$User\NTUSER.DAT"
$KeyRoot = "HKEY_USERS\$SID"

try {
    reg load "$KeyRoot" "$Hive" > $null
    Start-Sleep -Milliseconds 300
} catch {
    Write-Warning "[$(Get-Date)] Failed to load registry hive." | Out-File -Append $LogFile
    exit 1
}

# --- Додавання агенту в автозапуск ---
$RunKey = "Registry::$KeyRoot\Software\Microsoft\Windows\CurrentVersion\Run"
if (-not (Test-Path $RunKey)) { New-Item $RunKey -Force | Out-Null }

New-ItemProperty $RunKey -Name Agent -Value $RunCommand -Force

# --- Лагідне очищення автозапуску ---
$keepList = @('Agent')
foreach ($subKey in 'Run','RunOnce') {
    $rk = "Registry::$KeyRoot\Software\Microsoft\Windows\CurrentVersion\$subKey"
    if (Test-Path $rk) {
        Get-ItemProperty $rk |
        Select-Object -ExpandProperty PSObject.Properties |
        Where-Object { $_.Name -notin @('PSPath','PSParentPath','PSChildName','PSDrive','PSProvider') } |
        ForEach-Object {
            if ($keepList -notcontains $_.Name) {
                Write-Output "[$(Get-Date)] Removing $($_.Name) from $subKey" | Out-File -Append $LogFile
                Remove-ItemProperty $rk -Name $_.Name -ErrorAction SilentlyContinue
            }
        }
    }
}

# --- Залишити агент як shell, explorer.exe не запускається ---
$StartupShell = $AgentPath
$RunShellKey = "Registry::$KeyRoot\Software\Microsoft\Windows NT\CurrentVersion\Winlogon"

if (-not (Test-Path $RunShellKey)) { New-Item $RunShellKey -Force | Out-Null }
Set-ItemProperty $RunShellKey -Name Shell -Value $StartupShell -Force

# --- Unload hive ---
try {
    reg unload "$KeyRoot" > $null
    Write-Output "[$(Get-Date)] Registry hive unloaded successfully." | Out-File -Append $LogFile
} catch {
    Write-Warning "[$(Get-Date)] Failed to unload registry hive." | Out-File -Append $LogFile
}
