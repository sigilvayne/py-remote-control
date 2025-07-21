# Очистка тимчасових та безпечних файлів

$pathsToClean = @(
    "$env:TEMP",
    "C:\Windows\Temp",
    "C:\Windows\SoftwareDistribution\Download",
    "C:\Users\*\AppData\Local\Temp"
)

foreach ($path in $pathsToClean) {
    $expanded = Resolve-Path $path -ErrorAction SilentlyContinue
    foreach ($folder in $expanded) {
        Write-Host "Очищення: $folder"
        try {
            Get-ChildItem -Path $folder -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        } catch {
            Write-Warning "Не вдалося видалити деякі файли в $folder"
        }
    }
}

Write-Host "`nОчищення завершено."
