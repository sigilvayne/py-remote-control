# Перевірка та відновлення стану системних файлів Windows за допомогою DISM
Write-Host "=== Перевірка стану системи Windows ===" -ForegroundColor Green
Write-Host "Початок перевірки: $(Get-Date)" -ForegroundColor Yellow

try {
    # Перевірка цілісності системних файлів
    Write-Host "`nВиконується перевірка цілісності системних файлів..." -ForegroundColor Cyan
    $checkHealth = DISM.exe /Online /Cleanup-Image /CheckHealth
    
    Write-Host "`n=== Результати перевірки цілісності ===" -ForegroundColor Green
    foreach ($line in $checkHealth) {
        Write-Host $line
    }
    
    # Сканування системних файлів
    Write-Host "`nВиконується сканування системних файлів..." -ForegroundColor Cyan
    $scanHealth = DISM.exe /Online /Cleanup-Image /ScanHealth
    
    Write-Host "`n=== Результати сканування ===" -ForegroundColor Green
    foreach ($line in $scanHealth) {
        Write-Host $line
    }
    
    # Відновлення системних файлів (якщо потрібно)
    Write-Host "`nВиконується відновлення системних файлів..." -ForegroundColor Cyan
    $restoreHealth = DISM.exe /Online /Cleanup-Image /RestoreHealth
    
    Write-Host "`n=== Результати відновлення ===" -ForegroundColor Green
    foreach ($line in $restoreHealth) {
        Write-Host $line
    }
    
    # Перевірка стану компонентів
    Write-Host "`n=== Перевірка стану компонентів ===" -ForegroundColor Green
    $componentStatus = DISM.exe /Online /Get-WinCorruption
    
    Write-Host "`n=== Стан компонентів ===" -ForegroundColor Green
    foreach ($line in $componentStatus) {
        Write-Host $line
    }
    
    # Додаткова перевірка SFC
    Write-Host "`nВиконується додаткова перевірка SFC..." -ForegroundColor Cyan
    $sfcResult = sfc.exe /scannow
    
    Write-Host "`n=== Результати SFC ===" -ForegroundColor Green
    foreach ($line in $sfcResult) {
        Write-Host $line
    }
    
} catch {
    Write-Host "Помилка при виконанні перевірки стану: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nПеревірка стану завершена: $(Get-Date)" -ForegroundColor Yellow
