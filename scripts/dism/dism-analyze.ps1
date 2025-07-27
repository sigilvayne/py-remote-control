# Аналіз компонентного сховища Windows за допомогою DISM
Write-Host "=== Аналіз компонентного сховища Windows ===" -ForegroundColor Green
Write-Host "Початок аналізу: $(Get-Date)" -ForegroundColor Yellow

try {
    # Аналіз компонентного сховища
    Write-Host "`nВиконується аналіз компонентного сховища..." -ForegroundColor Cyan
    $analyzeResult = DISM.exe /Online /Cleanup-Image /AnalyzeComponentStore
    
    Write-Host "`n=== Результати аналізу компонентного сховища ===" -ForegroundColor Green
    foreach ($line in $analyzeResult) {
        Write-Host $line
    }
    
    # Додаткова інформація про розмір компонентного сховища
    Write-Host "`n=== Детальна інформація про компонентне сховище ===" -ForegroundColor Green
    
    $componentStore = Get-ChildItem -Path "C:\Windows\WinSxS" -ErrorAction SilentlyContinue
    if ($componentStore) {
        $totalSize = ($componentStore | Measure-Object -Property Length -Sum).Sum
        $sizeInGB = [math]::Round($totalSize / 1GB, 2)
        Write-Host "Розмір папки WinSxS: $sizeInGB GB"
    }
    
    # Перевірка доступного місця на диску C:
    $diskInfo = Get-PSDrive -Name C
    $freeSpaceGB = [math]::Round($diskInfo.Free / 1GB, 2)
    Write-Host "Вільне місце на диску C:: $freeSpaceGB GB"
    
} catch {
    Write-Host "Помилка при виконанні аналізу: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nАналіз завершено: $(Get-Date)" -ForegroundColor Yellow
