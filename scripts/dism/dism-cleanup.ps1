# Очистка компонентів Windows за допомогою DISM
Write-Host "=== Очистка компонентів Windows ===" -ForegroundColor Green
Write-Host "Початок очистки: $(Get-Date)" -ForegroundColor Yellow

try {
    # Перевірка доступного місця перед очисткою
    Write-Host "`n=== Перевірка дискового простору перед очисткою ===" -ForegroundColor Cyan
    $diskBefore = Get-PSDrive -Name C
    $freeSpaceBefore = [math]::Round($diskBefore.Free / 1GB, 2)
    Write-Host "Вільне місце на диску C: перед очисткою: $freeSpaceBefore GB"
    
    # Очистка компонентного сховища
    Write-Host "`nВиконується очистка компонентного сховища..." -ForegroundColor Cyan
    $cleanupResult = DISM.exe /Online /Cleanup-Image /StartComponentCleanup /ResetBase
    
    Write-Host "`n=== Результати очистки компонентного сховища ===" -ForegroundColor Green
    foreach ($line in $cleanupResult) {
        Write-Host $line
    }
    
    # Очистка застарілих пакетів
    Write-Host "`nВиконується очистка застарілих пакетів..." -ForegroundColor Cyan
    $packageCleanup = DISM.exe /Online /Cleanup-Image /StartComponentCleanup /ResetBase /Defer
    
    Write-Host "`n=== Результати очистки застарілих пакетів ===" -ForegroundColor Green
    foreach ($line in $packageCleanup) {
        Write-Host $line
    }
    
    # Перевірка доступного місця після очистки
    Write-Host "`n=== Перевірка дискового простору після очистки ===" -ForegroundColor Cyan
    Start-Sleep -Seconds 5  # Даємо час на завершення операцій
    $diskAfter = Get-PSDrive -Name C
    $freeSpaceAfter = [math]::Round($diskAfter.Free / 1GB, 2)
    $spaceFreed = $freeSpaceAfter - $freeSpaceBefore
    
    Write-Host "Вільне місце на диску C: після очистки: $freeSpaceAfter GB"
    Write-Host "Звільнено місця: $spaceFreed GB"
    
    # Очистка тимчасових файлів DISM
    Write-Host "`nВиконується очистка тимчасових файлів DISM..." -ForegroundColor Cyan
    $tempCleanup = DISM.exe /Online /Cleanup-Image /StartComponentCleanup /ResetBase /Defer
    
} catch {
    Write-Host "Помилка при виконанні очистки: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nОчистка завершена: $(Get-Date)" -ForegroundColor Yellow
