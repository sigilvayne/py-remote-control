# read-version-from-logs.ps1
$logDirs = @('C:\ProgramData\Medoc\Medoc\LOG', 'C:\ProgramData\Medoc\MedocSRV\LOG')
$pattern = 'update_*.log'

$logFiles = @()
foreach ($dir in $logDirs) {
    if (Test-Path $dir) {
        $logFiles += Get-ChildItem -Path $dir -Filter $pattern
    }
}
$logFiles = $logFiles | Sort-Object LastWriteTime -Descending

if (-not $logFiles) {
    Write-Error "No log files found matching pattern '$pattern' in any Medoc log directory."
    exit 1
}

$versionFound = $false

foreach ($file in $logFiles) {
    # Read last 20 lines from the file
    $lastLines = Get-Content -Path $file.FullName -Tail 20

    foreach ($line in $lastLines) {
        if ($line -match 'Версія програми - (\d+)') {
            $version = $matches[1]
            Write-Output "Found version $version in file: $($file.Name)"
            $versionFound = $true
            break
        }
    }

    if ($versionFound) {
        break
    }
}

if (-not $versionFound) {
    Write-Error "Version string 'Версія програми - <number>' not found in any log file."
    exit 1
}
