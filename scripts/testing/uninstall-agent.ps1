
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Output "Помилка: Потрібні права адміністратора для видалення агента"
    exit 1
}

$uninstallBatPath = "C:\Script\agent\uninstall.bat"

if (Test-Path $uninstallBatPath) {
    try {
        $process = Start-Process -FilePath $uninstallBatPath -Wait -PassThru -NoNewWindow
        if ($process.ExitCode -eq 0) {
            Write-Output "Службу агента зупинено успішно"
        } else {
            Write-Output "Службу агента зупинено з кодом виходу: $($process.ExitCode)"
        }
    } catch {
        Write-Output "Помилка запуску uninstall.bat: $($_.Exception.Message)"
    }
} else {
    Write-Output "Файл uninstall.bat не знайдено"
} 