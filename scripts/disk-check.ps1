# Оцінка розміру файлів, які можна безпечно видалити

$pathsToCheck = @(
    "$env:TEMP",
    "C:\Windows\Temp",
    "C:\Windows\SoftwareDistribution\Download",
    "C:\Users\*\AppData\Local\Temp"
)

$totalSizeBytes = 0

foreach ($path in $pathsToCheck) {
    $expanded = Resolve-Path $path -ErrorAction SilentlyContinue
    foreach ($folder in $expanded) {
        Write-Host "Аналізую: $folder"
        $files = Get-ChildItem -Path $folder -Recurse -ErrorAction SilentlyContinue -Force | Where-Object { -not $_.PSIsContainer }
        $size = ($files | Measure-Object -Property Length -Sum).Sum
        $totalSizeBytes += $size
    }
}

$totalSizeGB = [Math]::Round($totalSizeBytes / 1GB, 2)

Write-Host "`n=== Результат ==="
Write-Host "Загальна оцінка простору, який можна звільнити: $totalSizeGB GB"
