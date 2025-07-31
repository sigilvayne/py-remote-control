# Windows Defender Quick Scan Script
# This script runs a Windows Defender quick scan and outputs the results

Write-Output "Запуск швидкого сканування Windows Defender..."

try {
    # Check if Windows Defender is available
    $defenderStatus = Get-MpComputerStatus
    if (-not $defenderStatus) {
        Write-Output "Помилка: Windows Defender не знайдено на цій системі"
        exit 1
    }

    # Start quick scan
    Write-Output "Початок сканування..."
    $scanResult = Start-MpScan -ScanType QuickScan

    # Wait for scan to complete and get results
    Write-Output "Сканування завершено. Отримання результатів..."
    
    # Get the latest scan results
    $latestScan = Get-MpThreatDetection | Sort-Object InitialDetectionTime -Descending | Select-Object -First 10
    
    if ($latestScan) {
        Write-Output "Результати останнього сканування:"
        Write-Output "----------------------------------------"
        foreach ($threat in $latestScan) {
            Write-Output "Загроза: $($threat.ThreatName)"
            Write-Output "Файл: $($threat.FilePath)"
            Write-Output "Статус: $($threat.ActionSuccess)"
            Write-Output "Час виявлення: $($threat.InitialDetectionTime)"
            Write-Output "----------------------------------------"
        }
    } else {
        Write-Output "Загроз не виявлено."
    }

    # Get current protection status
    $protectionStatus = Get-MpComputerStatus
    Write-Output "Статус захисту:"
    Write-Output "- Антивірус: $($protectionStatus.AntivirusEnabled)"
    Write-Output "- Real-time protection: $($protectionStatus.RealTimeProtectionEnabled)"
    Write-Output "- Останнє оновлення: $($protectionStatus.AntivirusSignatureLastUpdated)"

} catch {
    Write-Output "Помилка під час сканування: $($_.Exception.Message)"
    exit 1
} 