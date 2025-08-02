$messages = @()

# Встановлюємо NuGet
try {
    Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -ErrorAction Stop
    $messages += "NuGet provider installed successfully."
} catch {
    $messages += "Failed to install NuGet provider: $_"
}

# Встановлюємо PSWindowsUpdate
try {
    Install-Module PSWindowsUpdate -Force -ErrorAction Stop
    $messages += "PSWindowsUpdate module installed successfully."
} catch {
    $messages += "Failed to install PSWindowsUpdate module: $_"
}

Write-Output ("PSWINDOWSUPDATE INSTALLATION REPORT:`n" + ($messages -join "`n"))
