param (
    [string]$url
)

if (-not $url) {
    Write-Error "URL не передано"
    exit 1
}

$tempPath = "C:\Script\agent\download"
New-Item -ItemType Directory -Force -Path $tempPath | Out-Null

# Визначаємо ім’я файлу та шлях до нього
$fileName = Split-Path -Leaf $url
$destination = Join-Path $tempPath $fileName

# Завантаження архіву
Invoke-WebRequest -Uri $url -OutFile $destination -UseBasicParsing
Write-Output "Завантажено: $destination"

# Тимчасова папка для розпакування
$tempUnzipDir = Join-Path $tempPath "unzipped_temp"
New-Item -ItemType Directory -Force -Path $tempUnzipDir | Out-Null

# Розпаковуємо архів у тимчасову папку
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory($destination, $tempUnzipDir)

Write-Output "Розпаковано у тимчасову папку: $tempUnzipDir"

# Переміщення вмісту з тимчасової папки до основної
Get-ChildItem -Path $tempUnzipDir -Recurse | ForEach-Object {
    $targetPath = Join-Path $tempPath ($_.FullName.Substring($tempUnzipDir.Length).TrimStart('\'))
    $targetDir = Split-Path -Path $targetPath -Parent
    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
    }
    Move-Item -Path $_.FullName -Destination $targetPath
}

# Видалення тимчасової папки
Remove-Item -Path $tempUnzipDir -Recurse -Force

# Перевірка файлів
$files = Get-ChildItem -Path $tempPath -Recurse -File | Where-Object { $_.FullName -ne $destination }
if ($files.Count -eq 0) {
    Write-Warning "Увага: архів порожній або не містить файлів"
} else {
    Write-Output "Файли в архіві:"
    $files | ForEach-Object { Write-Output ("- " + $_.FullName) }
}
